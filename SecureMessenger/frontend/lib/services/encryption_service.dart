// lib/services/encryption_service.dart
import 'dart:convert';
import 'dart:io';
import 'dart:math';

import 'package:cryptography/cryptography.dart';
import 'package:path_provider/path_provider.dart';

class EncryptionService {
  // AEAD: XChaCha20-Poly1305 (nonce=24, tag=16)
  static final Xchacha20 _aead = Xchacha20.poly1305Aead();

  // Encabezado simple para marcar blobs/grafo interno
  static final List<int> _magic = utf8.encode('SM1');

  // RNG
  static final _rng = Random.secure();

  // ============================ E2E: Texto ============================

  static Future<String> encryptText(String clear, int chatId) async {
    final keyBytes = await _loadChatKeyOrThrow(chatId);
    final secretKey = SecretKey(keyBytes);
    final nonce = _randomBytes(24); // 24 bytes para XChaCha20
    final box = await _aead.encrypt(
      utf8.encode(clear),
      secretKey: secretKey,
      nonce: nonce,
    );
    // Ensamblamos: "SM1" | nonce(24) | ciphertext | tag(16)
    final out = <int>[]
      ..addAll(_magic)
      ..addAll(nonce)
      ..addAll(box.cipherText)
      ..addAll(box.mac.bytes);
    return base64Encode(out);
  }

  static Future<String> decryptText(String b64, int chatId) async {
    final data = base64Decode(b64);
    final msg = _parseSm1(data); // extrae nonce, cipher, mac
    final keyBytes = await _loadChatKeyOrThrow(chatId);
    final secretKey = SecretKey(keyBytes);
    final clear = await _aead.decrypt(
      SecretBox(msg.cipherText, nonce: msg.nonce, mac: Mac(msg.mac)),
      secretKey: secretKey,
    );
    return utf8.decode(clear);
  }

  // ============================ E2E: Archivos ============================

  /// Lee todo a memoria (suficiente para pruebas). Para producción, migrar a streams.
  static Future<File> encryptFile({
    required File input,
    required int chatId,
    required String outputPath,
  }) async {
    final keyBytes = await _loadChatKeyOrThrow(chatId);
    final secretKey = SecretKey(keyBytes);
    final nonce = _randomBytes(24);

    final clear = await input.readAsBytes();
    final box = await _aead.encrypt(clear, secretKey: secretKey, nonce: nonce);

    final out = <int>[]
      ..addAll(_magic)
      ..addAll(nonce)
      ..addAll(box.cipherText)
      ..addAll(box.mac.bytes);

    final f = File(outputPath);
    await f.writeAsBytes(out, flush: true);
    return f;
  }

  static Future<File> decryptFile({
    required File input,
    required int chatId,
    required String outputPath,
  }) async {
    final bytes = await input.readAsBytes();
    final msg = _parseSm1(bytes);

    final keyBytes = await _loadChatKeyOrThrow(chatId);
    final secretKey = SecretKey(keyBytes);
    final clear = await _aead.decrypt(
      SecretBox(msg.cipherText, nonce: msg.nonce, mac: Mac(msg.mac)),
      secretKey: secretKey,
    );

    final f = File(outputPath);
    await f.writeAsBytes(clear, flush: true);
    return f;
  }

  // ============================ Gestión de claves ============================

  /// ¿ya existe clave E2E para este chat?
  static Future<bool> hasChatKey(int chatId) async {
    final file = await _keyFile(chatId);
    return file.exists();
  }

  /// Guarda clave E2E (32 bytes).
  static Future<void> setChatKey(int chatId, List<int> key) async {
    if (key.length != 32) {
      throw ArgumentError('Chat key debe ser de 32 bytes');
    }
    final file = await _keyFile(chatId);
    await file.create(recursive: true);
    await file.writeAsBytes(key, flush: true);
  }

  /// Carga la clave E2E o lanza si no existe.
  static Future<List<int>> _loadChatKeyOrThrow(int chatId) async {
    final file = await _keyFile(chatId);
    if (!await file.exists()) {
      throw StateError('No hay clave E2E para chat $chatId');
    }
    return await file.readAsBytes();
  }

  // ---------- Privada efímera del creador (Base64), hasta derivar ----------
  static Future<void> saveChatPriv(int chatId, String privB64) async {
    final f = await _privFile(chatId);
    await f.create(recursive: true);
    await f.writeAsString(privB64, flush: true);
  }

  static Future<String?> loadChatPriv(int chatId) async {
    final f = await _privFile(chatId);
    if (!await f.exists()) return null;
    return f.readAsString();
  }

  static Future<void> deleteChatPriv(int chatId) async {
    final f = await _privFile(chatId);
    if (await f.exists()) {
      try {
        // Best effort wipe
        final bytes = await f.readAsBytes();
        for (var i = 0; i < bytes.length; i++) {
          bytes[i] = _rng.nextInt(256);
        }
        await f.writeAsBytes(bytes, flush: true);
      } catch (_) {}
      await f.delete();
    }
  }

  // ============================ ECDH X25519 + HKDF ============================

  /// Genera un par X25519 y devuelve:
  ///  - 'priv' Base64 (32 bytes de semilla)
  ///  - 'pub'  Base64 (32 bytes)
  static Future<Map<String, String>> generateX25519KeyPair() async {
    final seed = _randomBytes(32); // 32 bytes
    final alg = X25519();
    final keyPair = await alg.newKeyPairFromSeed(seed);
    final pub = await keyPair.extractPublicKey();
    return {
      'priv': base64Encode(seed),
      'pub' : base64Encode(pub.bytes),
    };
  }

  /// Deriva la clave de chat con ECDH X25519 + HKDF-SHA256 (32 bytes).
  /// - [myPrivB64]: tu privada (32 bytes) en Base64
  /// - [otherPubB64]: pública del otro (32 bytes) en Base64
  static Future<List<int>> deriveChatKeyFromECDH({
    required String myPrivB64,
    required String otherPubB64,
  }) async {
    final alg = X25519();
    final mySeed = base64Decode(myPrivB64); // 32 bytes
    final myKeyPair = await alg.newKeyPairFromSeed(mySeed);

    final otherPub = SimplePublicKey(
      base64Decode(otherPubB64),
      type: KeyPairType.x25519,
    );

    final sharedSecret = await alg.sharedSecretKey(
      keyPair: myKeyPair,
      remotePublicKey: otherPub,
    );
    final sharedBytes = await sharedSecret.extractBytes();

    // HKDF con SHA-256 -> 32 bytes de clave simétrica
    final hkdf = Hkdf(hmac: Hmac.sha256(), outputLength: 32);
    final derived = await hkdf.deriveKey(
      secretKey: SecretKey(sharedBytes),
      info: utf8.encode('SM1-CHAT-KEY'),
    );
    return await derived.extractBytes(); // 32B
  }

  // ============================ Utilidades ============================

  static Future<File> _keyFile(int chatId) async {
    final dir = await _appDir();
    return File('${dir.path}/keys/chat_$chatId.key');
  }

  static Future<File> _privFile(int chatId) async {
    final dir = await _appDir();
    return File('${dir.path}/keys/chat_$chatId.priv');
  }

  static Future<Directory> _appDir() async {
    final d = await getApplicationDocumentsDirectory();
    final app = Directory('${d.path}/secure_messenger');
    if (!await app.exists()) {
      await app.create(recursive: true);
    }
    return app;
  }

  /// Borrado a mejor esfuerzo (una pasada aleatoria + delete).
  static Future<void> secureDelete(File f) async {
    try {
      final len = await f.length();
      final raf = await f.open(mode: FileMode.write);
      const block = 64 * 1024;
      final buf = List<int>.filled(block, 0);
      int written = 0;
      while (written < len) {
        for (var i = 0; i < buf.length; i++) {
          buf[i] = _rng.nextInt(256);
        }
        final toWrite = (len - written) < block ? (len - written).toInt() : block;
        await raf.writeFrom(buf, 0, toWrite);
        written += toWrite;
      }
      await raf.flush();
      await raf.close();
    } catch (_) {}
    try { await f.delete(); } catch (_) {}
  }

  static List<int> _randomBytes(int n) =>
      List<int>.generate(n, (_) => _rng.nextInt(256));

  // Parser del contenedor SM1
  static _Sm1Parts _parseSm1(List<int> data) {
    if (data.length < 3 + 24 + 16) {
      throw const FormatException('SM1: tamaño inválido');
    }
    if (!(data[0] == _magic[0] && data[1] == _magic[1] && data[2] == _magic[2])) {
      throw const FormatException('SM1: encabezado inválido');
    }
    final nonce = data.sublist(3, 3 + 24);
    final mac = data.sublist(data.length - 16);
    final cipher = data.sublist(3 + 24, data.length - 16);
    return _Sm1Parts(nonce: nonce, cipherText: cipher, mac: mac);
  }
}

class _Sm1Parts {
  final List<int> nonce;
  final List<int> cipherText;
  final List<int> mac;
  _Sm1Parts({required this.nonce, required this.cipherText, required this.mac});
}
