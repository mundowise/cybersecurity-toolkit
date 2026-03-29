import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';

import '../models/chat.dart';
import '../models/message.dart';
import 'encryption_service.dart';

class ApiService {
  // Ajusta si cambias de máquina/backend
  static const String baseUrl = "http://192.168.0.104:8000";

  // -------- AUTH --------
  static Future<Map<String, dynamic>> register(String alias, String password) async {
    final res = await http.post(
      Uri.parse("$baseUrl/auth/register"),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'alias': alias, 'password': password}),
    );
    if (res.statusCode != 200 && res.statusCode != 201) {
      throw Exception("Register failed: ${res.body}");
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  static Future<Map<String, dynamic>> login(String alias, String password) async {
    final res = await http.post(
      Uri.parse("$baseUrl/auth/login"),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'alias': alias, 'password': password}),
    );
    if (res.statusCode != 200) {
      throw Exception("Login failed: ${res.body}");
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  // -------- CHATS --------
  static Future<List<Chat>> getChats(String token) async {
    final res = await http.get(
      Uri.parse("$baseUrl/chat/list"),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (res.statusCode != 200) {
      throw Exception("Error fetching chats: ${res.body}");
    }
    final list = jsonDecode(res.body) as List<dynamic>;
    return list.map((e) => Chat.fromJson(e as Map<String, dynamic>)).toList();
  }

  static Future<Chat> createChat(
    String token,
    List<int> memberIds, {
    bool isGroup = false,
    String? name,
  }) async {
    final res = await http.post(
      Uri.parse("$baseUrl/chat/create"),
      headers: {'Authorization': 'Bearer $token', 'Content-Type': 'application/json'},
      body: jsonEncode({'is_group': isGroup, 'name': name, 'members': memberIds}),
    );
    if (res.statusCode != 200) {
      throw Exception("Create chat failed: ${res.body}");
    }
    return Chat.fromJson(jsonDecode(res.body));
  }

  static Future<List<Message>> getMessages(String token, int chatId) async {
    final res = await http.get(
      Uri.parse("$baseUrl/chat/messages/$chatId"),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (res.statusCode != 200) {
      throw Exception("Get messages failed: ${res.body}");
    }
    final list = (jsonDecode(res.body) as List).map((e) => Message.fromJson(e)).toList();

    // Descifrar los de texto en cliente
    final dec = <Message>[];
    for (final m in list) {
      if (m.type == 'text' && m.content.isNotEmpty) {
        try {
          final clear = await EncryptionService.decryptText(m.content, m.chatId);
          dec.add(m.copyWith(content: clear));
        } catch (_) {
          dec.add(m);
        }
      } else {
        dec.add(m);
      }
    }
    return dec;
  }

  static Future<Message> sendMessage(String token, Message message) async {
    String payloadContent = message.content;
    if (message.type == 'text') {
      payloadContent = await EncryptionService.encryptText(message.content, message.chatId);
    }
    final res = await http.post(
      Uri.parse("$baseUrl/chat/message/send"),
      headers: {'Authorization': 'Bearer $token', 'Content-Type': 'application/json'},
      body: jsonEncode({
        'chat_id': message.chatId,
        'content': payloadContent,
        'expires_at': message.expiresAt, // ISO8601 o null
        'type': message.type,
        'filename': message.filename,
        'mimetype': message.mimetype,
      }),
    );
    if (res.statusCode != 200) {
      throw Exception("Error sending message: ${res.body}");
    }
    final msg = Message.fromJson(jsonDecode(res.body));
    if (msg.type == 'text' && msg.content.isNotEmpty) {
      try {
        final clear = await EncryptionService.decryptText(msg.content, msg.chatId);
        return msg.copyWith(content: clear);
      } catch (_) {
        return msg;
      }
    }
    return msg;
  }

  // -------- FILES (SIEMPRE CIFRADOS) --------
  static Future<String> uploadFileEncrypted({
    required String token,
    required int chatId,
    required File file,
    required String filename,
    required String mimetype,
  }) async {
    final tmpDir = await getTemporaryDirectory();
    final encPath = '${tmpDir.path}/$filename.sm1';
    final encFile = await EncryptionService.encryptFile(input: file, chatId: chatId, outputPath: encPath);

    final req = http.MultipartRequest('POST', Uri.parse("$baseUrl/files/upload"));
    req.headers['Authorization'] = 'Bearer $token';
    req.fields['chat_id'] = '$chatId';
    req.fields['filename'] = '$filename.sm1';
    req.files.add(await http.MultipartFile.fromPath('file', encFile.path));

    final res = await req.send();
    final body = await res.stream.bytesToString();
    try { await encFile.delete(); } catch (_) {}
    if (res.statusCode != 200) {
      throw Exception("Upload failed: $body");
    }
    final map = jsonDecode(body) as Map<String, dynamic>;
    return map['file_id'] as String;
  }

  static Future<File> downloadFileDecrypted({
    required String token,
    required int chatId,
    required String fileId,
    required String savePath,
  }) async {
    final res = await http.get(
      Uri.parse("$baseUrl/files/download/$fileId"),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (res.statusCode != 200) {
      throw Exception("Download failed: ${res.body}");
    }
    final tmp = File('$savePath.cipher');
    await tmp.writeAsBytes(res.bodyBytes);
    final plain = await EncryptionService.decryptFile(input: tmp, chatId: chatId, outputPath: savePath);
    try { await tmp.delete(); } catch (_) {}
    return plain;
  }

  static Future<Message> sendEncryptedFileMessage({
    required String token,
    required int chatId,
    required File file,
    required String filename,
    String mimetype = 'application/octet-stream+sm1',
    String? expiresAt,
  }) async {
    final fid = await uploadFileEncrypted(
      token: token, chatId: chatId, file: file, filename: filename, mimetype: mimetype,
    );
    final msg = Message(
      id: 0,
      chatId: chatId,
      senderId: 0,
      content: fid,
      sentAt: '',
      expiresAt: expiresAt,
      type: 'file',
      filename: filename.endsWith('.sm1') ? filename : '$filename.sm1',
      mimetype: 'application/octet-stream+sm1',
    );
    return await sendMessage(token, msg);
  }

  // -------- VOICE (SIEMPRE CIFRADO) --------
  static Future<String> uploadVoiceEncrypted({
    required String token,
    required int chatId,
    required File opusFile,
    required String filename,
  }) async {
    final tmpDir = await getTemporaryDirectory();
    final encPath = '${tmpDir.path}/$filename';
    final encFile = await EncryptionService.encryptFile(input: opusFile, chatId: chatId, outputPath: encPath);

    final req = http.MultipartRequest('POST', Uri.parse("$baseUrl/voice/upload"));
    req.headers['Authorization'] = 'Bearer $token';
    req.fields['chat_id'] = '$chatId';
    req.fields['filename'] = filename;
    req.files.add(await http.MultipartFile.fromPath('file', encFile.path));

    final res = await req.send();
    final body = await res.stream.bytesToString();
    try { await encFile.delete(); } catch (_) {}
    if (res.statusCode != 200) {
      throw Exception("Upload voice failed: $body");
    }
    final map = jsonDecode(body) as Map<String, dynamic>;
    return map['voice_id'] as String;
  }

  static Future<File> downloadVoiceDecrypted({
    required String token,
    required int chatId,
    required String voiceId,
    required String savePath,
  }) async {
    final res = await http.get(
      Uri.parse("$baseUrl/voice/download/$voiceId"),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (res.statusCode != 200) {
      throw Exception("Download voice failed: ${res.body}");
    }
    final tmp = File('$savePath.cipher');
    await tmp.writeAsBytes(res.bodyBytes);
    final plain = await EncryptionService.decryptFile(input: tmp, chatId: chatId, outputPath: savePath);
    try { await tmp.delete(); } catch (_) {}
    return plain;
  }

  static Future<Message> sendEncryptedVoiceMessage({
    required String token,
    required int chatId,
    required File opusFile,
    String filename = 'voice.opus.sm1',
    String? expiresAt,
  }) async {
    final vid = await uploadVoiceEncrypted(
      token: token, chatId: chatId, opusFile: opusFile, filename: filename,
    );
    final msg = Message(
      id: 0,
      chatId: chatId,
      senderId: 0,
      content: vid,
      sentAt: '',
      expiresAt: expiresAt,
      type: 'voice',
      filename: filename,
      mimetype: 'audio/opus+sm1',
    );
    return await sendMessage(token, msg);
  }

  // --- Invitaciones con ECDH ---
  static Future<Map<String, dynamic>> createInvite({
    required String token,
    required bool isGroup,
    String? name,
    required String creatorPubKeyB64,
    int ttlMinutes = 15,
  }) async {
    final res = await http.post(
      Uri.parse("$baseUrl/invites/create"),
      headers: {'Authorization': 'Bearer $token', 'Content-Type': 'application/json'},
      body: jsonEncode({
        'ttl_minutes': ttlMinutes,
        'is_group': isGroup,
        'name': name,
        'creator_pubkey': creatorPubKeyB64,
      }),
    );
    if (res.statusCode != 200) {
      throw Exception("createInvite failed: ${res.body}");
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  static Future<Map<String, dynamic>> redeemInvite({
    required String token,
    required String code,
    required String redeemerPubKeyB64,
  }) async {
    final res = await http.post(
      Uri.parse("$baseUrl/invites/redeem"),
      headers: {'Authorization': 'Bearer $token', 'Content-Type': 'application/json'},
      body: jsonEncode({'code': code, 'redeemer_pubkey': redeemerPubKeyB64}),
    );
    if (res.statusCode != 200) {
      throw Exception("redeemInvite failed: ${res.body}");
    }
    return jsonDecode(res.body) as Map<String, dynamic>; // {chat_id, other_pubkey}
  }

  static Future<List<Map<String, dynamic>>> getKeyInfo({
    required String token,
    required int chatId,
  }) async {
    final res = await http.get(
      Uri.parse("$baseUrl/chat/keyinfo/$chatId"),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (res.statusCode != 200) {
      throw Exception("getKeyInfo failed: ${res.body}");
    }
    final map = jsonDecode(res.body) as Map<String, dynamic>;
    return (map['keys'] as List).cast<Map<String, dynamic>>();
  }

  // --- Alias por chat ---
  static Future<void> setChatAlias({
    required String token,
    required int chatId,
    required String displayName,
  }) async {
    final res = await http.post(
      Uri.parse("$baseUrl/chat/alias"),
      headers: {'Authorization': 'Bearer $token', 'Content-Type': 'application/json'},
      body: jsonEncode({'chat_id': chatId, 'display_name': displayName}),
    );
    if (res.statusCode != 200) {
      throw Exception("setChatAlias failed: ${res.body}");
    }
  }

  // --- Fingerprint + meta ---
  static Future<Map<String, dynamic>> getChatMeta({
    required String token,
    required int chatId,
  }) async {
    final res = await http.get(
      Uri.parse("$baseUrl/chat/meta/$chatId"),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (res.statusCode != 200) {
      throw Exception("getChatMeta failed: ${res.body}");
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }

  // --- Limpiar chat (borrar historial, mantener chat) ---
  static Future<Map<String, dynamic>> clearChat({
    required String token,
    required int chatId,
  }) async {
    final res = await http.post(
      Uri.parse("$baseUrl/chat/clear/$chatId"),
      headers: {'Authorization': 'Bearer $token'},
    );
    if (res.statusCode != 200) {
      throw Exception("clearChat failed: ${res.body}");
    }
    return jsonDecode(res.body) as Map<String, dynamic>;
  }
}
