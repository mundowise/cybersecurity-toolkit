import 'dart:io';
import 'dart:math';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:provider/provider.dart';
import 'package:record/record.dart';
import 'package:ffmpeg_kit_flutter_full_gpl/ffmpeg_kit.dart';
import 'package:ffmpeg_kit_flutter_full_gpl/return_code.dart';

import '../models/chat.dart';
import '../models/message.dart';
import '../providers/auth_provider.dart';
import '../providers/chat_provider.dart';
import '../services/api_service.dart';
import '../services/encryption_service.dart';

class ChatScreen extends StatefulWidget {
  final Chat chat;
  const ChatScreen({super.key, required this.chat});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _textCtrl = TextEditingController();
  final ScrollController _scroll = ScrollController();

  final AudioRecorder _rec = AudioRecorder();
  bool _recording = false;

  bool _sending = false;
  bool _busy = false;

  // Meta
  String? _fingerprint;
  String? _myAlias;     // cómo te ven en este chat
  String? _theirAlias;  // cómo ves al otro (sólo 1:1)

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final auth = context.read<AuthProvider>();
      await context.read<ChatProvider>().loadMessages(auth.token!, widget.chat.id);
      await _loadMeta();
      await _ensureChatKey(); // <- asegura la clave E2E si eres el creador
      _scrollToBottom();
    });
  }

  Future<void> _loadMeta() async {
    try {
      final auth = context.read<AuthProvider>();
      final meta = await ApiService.getChatMeta(token: auth.token!, chatId: widget.chat.id);
      setState(() {
        _fingerprint = meta['fingerprint']?.toString();
        final isGroup = (meta['is_group'] as bool?) ?? false;
        if (!isGroup) {
          final members = (meta['members'] as List).cast<Map<String, dynamic>>();
          if (members.length == 2) {
            final me = members.firstWhere((m) => m['user_id'] == auth.userId, orElse: () => {});
            final other = members.firstWhere((m) => m['user_id'] != auth.userId, orElse: () => {});
            _myAlias = (me['display_name'] as String?)?.trim();
            _theirAlias = (other['display_name'] as String?)?.trim();
          }
        }
      });
    } catch (_) {
      // meta opcional; ignoramos si falla
    }
  }

  // Si eres el creador: deriva la clave cuando el otro ya registró su pubkey
  Future<void> _ensureChatKey() async {
    final has = await EncryptionService.hasChatKey(widget.chat.id);
    if (has) return;

    final auth = context.read<AuthProvider>();
    final priv = await EncryptionService.loadChatPriv(widget.chat.id);
    if (priv == null) return; // no eres el creador o ya se derivó

    try {
      final infos = await ApiService.getKeyInfo(token: auth.token!, chatId: widget.chat.id);
      final other = infos.firstWhere((k) => k['user_id'] != auth.userId, orElse: () => {});
      final otherPub = (other['pubkey'] as String?) ?? '';
      if (otherPub.isEmpty) return;

      final key = await EncryptionService.deriveChatKeyFromECDH(
        myPrivB64: priv,
        otherPubB64: otherPub,
      );
      await EncryptionService.setChatKey(widget.chat.id, key);
      await EncryptionService.deleteChatPriv(widget.chat.id);
    } catch (_) {
      // silencioso, reintenta al volver a abrir
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scroll.hasClients) {
        _scroll.jumpTo(_scroll.position.maxScrollExtent);
      }
    });
  }

  // ===================== Texto (E2E) =====================
  Future<void> _sendText() async {
    final auth = context.read<AuthProvider>();
    final provider = context.read<ChatProvider>();
    final content = _textCtrl.text.trim();
    if (content.isEmpty) return;

    setState(() => _sending = true);
    try {
      final msg = Message(
        id: 0,
        chatId: widget.chat.id,
        senderId: 0,
        content: content, // ApiService lo cifra
        sentAt: '',
        expiresAt: null,
        type: 'text',
        filename: null,
        mimetype: null,
      );
      await ApiService.sendMessage(auth.token!, msg);
      await provider.loadMessages(auth.token!, widget.chat.id);
      _textCtrl.clear();
      _scrollToBottom();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error enviando: $e')));
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  // ===================== Archivos (E2E .sm1) =====================
  Future<void> _pickAndSendFile() async {
    final auth = context.read<AuthProvider>();
    final provider = context.read<ChatProvider>();

    final res = await FilePicker.platform.pickFiles(withReadStream: false);
    if (res == null || res.files.isEmpty) return;

    final f = res.files.single;
    if (f.path == null) return;
    final file = File(f.path!);
    final filename = f.name;

    setState(() => _busy = true);
    try {
      await ApiService.sendEncryptedFileMessage(
        token: auth.token!,
        chatId: widget.chat.id,
        file: file,
        filename: filename,
      );
      await provider.loadMessages(auth.token!, widget.chat.id);
      _scrollToBottom();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error archivo: $e')));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _downloadFile(String fileId, String filename) async {
    try {
      final auth = context.read<AuthProvider>();
      Directory? base = await getDownloadsDirectory();
      base ??= await getApplicationDocumentsDirectory();
      final savePath = '${base.path}/$filename';
      await ApiService.downloadFileDecrypted(
        token: auth.token!,
        chatId: widget.chat.id,
        fileId: fileId,
        savePath: savePath,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Descargado en:\n$savePath')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error al descargar: $e')));
    }
  }

  // ===================== Voz (grabar -> distorsionar -> cifrar -> subir) =====================
  Future<void> _toggleRecord() async {
    final auth = context.read<AuthProvider>();
    final provider = context.read<ChatProvider>();

    if (!_recording) {
      try {
        final hasPerm = await _rec.hasPermission();
        if (!hasPerm) throw Exception('Permiso de micrófono denegado');
        final dir = await getTemporaryDirectory();
        final wavPath = '${dir.path}/rec_${DateTime.now().millisecondsSinceEpoch}.wav';
        await _rec.start(
          const RecordConfig(encoder: AudioEncoder.wav, sampleRate: 48000, numChannels: 1),
          path: wavPath,
        );
        setState(() => _recording = true);
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('No se pudo grabar: $e')));
      }
      return;
    }

    // Detener y procesar
    setState(() => _recording = false);
    setState(() => _busy = true);
    try {
      final recPath = await _rec.stop();
      if (recPath == null) throw Exception('No hay archivo de grabación');
      final raw = File(recPath);

      // 1) Distorsionar + Opus
      final tmpDir = await getTemporaryDirectory();
      final opusPath = '${tmpDir.path}/voice_${_rand()}.opus';
      await _distortToOpus(inPath: raw.path, outPath: opusPath);

      // 2) Subir cifrado y crear mensaje
      await ApiService.sendEncryptedVoiceMessage(
        token: auth.token!,
        chatId: widget.chat.id,
        opusFile: File(opusPath),
        filename: 'voice.opus.sm1',
      );

      // 3) Borrado best-effort
      try { await EncryptionService.secureDelete(raw); } catch (_) {}
      try { await EncryptionService.secureDelete(File(opusPath)); } catch (_) {}

      await provider.loadMessages(auth.token!, widget.chat.id);
      _scrollToBottom();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Voz: $e')));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _downloadVoice(String voiceId) async {
    try {
      final auth = context.read<AuthProvider>();
      Directory? base = await getDownloadsDirectory();
      base ??= await getApplicationDocumentsDirectory();
      final savePath = '${base.path}/voice_${DateTime.now().millisecondsSinceEpoch}.opus';
      await ApiService.downloadVoiceDecrypted(
        token: auth.token!,
        chatId: widget.chat.id,
        voiceId: voiceId,
        savePath: savePath,
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error al descargar voz: $e')));
      return;
    }
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Voz guardada en Descargas')));
  }

  Future<void> _distortToOpus({required String inPath, required String outPath}) async {
    final args = [
      '-y',
      '-i', inPath,
      '-af',
      'asetrate=48000*1.15,aresample=48000,atempo=0.87,highpass=f=300,lowpass=f=3200,acrusher=bits=8:mode=log:aa=1',
      '-c:a', 'libopus',
      '-b:a', '24k',
      outPath,
    ];

    if (_isMobileOrMacOS()) {
      final session = await FFmpegKit.execute(args.join(' '));
      final rc = await session.getReturnCode();
      if (!ReturnCode.isSuccess(rc)) {
        final logs = await session.getLogsAsString();
        throw Exception('ffmpeg_kit failed: rc=$rc logs=$logs');
      }
    } else {
      final proc = await Process.start('ffmpeg', args);
      final code = await proc.exitCode;
      if (code != 0) {
        final err = await proc.stderr.transform(const SystemEncoding().decoder).join();
        throw Exception('ffmpeg failed ($code): $err');
      }
    }

    if (!await File(outPath).exists()) {
      throw Exception('No se generó el opus distorsionado');
    }
  }

  bool _isMobileOrMacOS() {
    try {
      return Platform.isAndroid || Platform.isIOS || Platform.isMacOS || Platform.isWindows;
    } catch (_) {
      return false;
    }
  }

  String _rand() => Random.secure().nextInt(1 << 32).toRadixString(16);

  @override
  Widget build(BuildContext context) {
    final msgs = context.watch<ChatProvider>().messages[widget.chat.id] ?? [];
    final cs = Theme.of(context).colorScheme;
    final titleText = widget.chat.name ??
        (widget.chat.isGroup ? 'Grupo' : (_theirAlias?.isNotEmpty == true ? _theirAlias! : 'Chat'));

    return Scaffold(
      backgroundColor: cs.background,
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(titleText),
            if (_fingerprint != null)
              Text('FP: $_fingerprint', style: Theme.of(context).textTheme.bodySmall),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.copy_all),
            tooltip: 'Copiar fingerprint',
            onPressed: _fingerprint == null
                ? null
                : () async {
                    final fp = _fingerprint;
                    if (fp == null) return;
                    await Clipboard.setData(ClipboardData(text: fp));
                    if (!mounted) return;
                    ScaffoldMessenger.of(context)
                        .showSnackBar(const SnackBar(content: Text('Fingerprint copiado')));
                  },
          ),
          PopupMenuButton<String>(
            onSelected: (v) async {
              if (v == 'alias') {
                final ctrl = TextEditingController(text: _myAlias ?? '');
                final val = await showDialog<String>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Tu alias en este chat'),
                    content: TextField(
                      controller: ctrl,
                      decoration: const InputDecoration(hintText: 'Cómo quieres que te vean'),
                    ),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
                      FilledButton(onPressed: () => Navigator.pop(ctx, ctrl.text.trim()), child: const Text('Guardar')),
                    ],
                  ),
                );
                if (val != null) {
                  final auth = context.read<AuthProvider>();
                  await ApiService.setChatAlias(token: auth.token!, chatId: widget.chat.id, displayName: val);
                  setState(() => _myAlias = val);
                }
              } else if (v == 'clear') {
                final ok = await showDialog<bool>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Limpiar chat'),
                    content: const Text(
                        'Esto borrará TODO el historial (mensajes y archivos) de este chat en el servidor. ¿Continuar?'),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
                      FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Borrar')),
                    ],
                  ),
                );
                if (ok == true) {
                  final auth = context.read<AuthProvider>();
                  await ApiService.clearChat(token: auth.token!, chatId: widget.chat.id);
                  await context.read<ChatProvider>().loadMessages(auth.token!, widget.chat.id);
                  if (!mounted) return;
                  ScaffoldMessenger.of(context)
                      .showSnackBar(const SnackBar(content: Text('Historial borrado')));
                }
              }
            },
            itemBuilder: (ctx) => const [
              PopupMenuItem(value: 'alias', child: Text('Editar mi alias')),
              PopupMenuItem(value: 'clear', child: Text('Limpiar chat')),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scroll,
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
              itemCount: msgs.length,
              itemBuilder: (ctx, i) {
                final m = msgs[i];
                final isFile = m.type == 'file';
                final isVoice = m.type == 'voice';
                final mine = m.senderId == context.read<AuthProvider>().userId;

                final bubbleColor = mine ? cs.primaryContainer : cs.surfaceVariant;
                final textColor = Colors.white.withOpacity(0.92);
                final leadingIcon = isFile
                    ? Icons.broken_image_outlined
                    : isVoice
                        ? Icons.graphic_eq
                        : Icons.terminal_rounded;

                return Align(
                  alignment: mine ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: bubbleColor,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.35),
                          blurRadius: 8,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Icon(leadingIcon, size: 18, color: cs.primary),
                        const SizedBox(width: 8),
                        if (isFile)
                          Flexible(child: Text(m.filename ?? 'Archivo', style: TextStyle(color: textColor)))
                        else if (isVoice)
                          const Flexible(child: Text('Mensaje de voz', style: TextStyle(color: Colors.white)))
                        else
                          Flexible(child: Text(m.content, style: TextStyle(color: textColor))),
                        const SizedBox(width: 8),
                        if (isFile)
                          TextButton.icon(
                            onPressed: () => _downloadFile(m.content, m.filename ?? 'archivo.sm1'),
                            icon: const Icon(Icons.download),
                            label: const Text('Descargar'),
                          )
                        else if (isVoice)
                          TextButton.icon(
                            onPressed: () => _downloadVoice(m.content),
                            icon: const Icon(Icons.download),
                            label: const Text('Guardar'),
                          ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          const Divider(height: 1),
          SafeArea(
            top: false,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.attach_file),
                    onPressed: _sending || _busy ? null : _pickAndSendFile,
                    tooltip: 'Adjuntar archivo',
                  ),
                  Expanded(
                    child: TextField(
                      controller: _textCtrl,
                      minLines: 1,
                      maxLines: 5,
                      decoration: const InputDecoration(
                        hintText: 'Escribe un mensaje…',
                        isDense: true,
                        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      ),
                      onSubmitted: (_) => _sendText(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: _busy
                        ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                        : Icon(_recording ? Icons.stop : Icons.mic),
                    color: _recording ? Colors.red : null,
                    onPressed: _busy ? null : _toggleRecord,
                    tooltip: _recording ? 'Detener y enviar' : 'Grabar voz',
                  ),
                  const SizedBox(width: 4),
                  IconButton(
                    icon: const Icon(Icons.send),
                    onPressed: _sending || _busy ? null : _sendText,
                    tooltip: 'Enviar texto',
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
