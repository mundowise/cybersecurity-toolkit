import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import '../services/encryption_service.dart';

class NewChatScreen extends StatefulWidget {
  const NewChatScreen({super.key});

  @override
  State<NewChatScreen> createState() => _NewChatScreenState();
}

class _NewChatScreenState extends State<NewChatScreen> with SingleTickerProviderStateMixin {
  late final TabController _tab = TabController(length: 2, vsync: this);

  // crear invitación
  bool _group = false;
  final _nameCtrl = TextEditingController();
  String? _code;
  String? _uri;
  String? _expires;
  int? _chatId;
  String? _myPrivB64; // privada del creador (temporal)
  bool _busyCreate = false;

  // unirse
  final _codeCtrl = TextEditingController();
  bool _busyJoin = false;

  @override
  void dispose() {
    _tab.dispose();
    _nameCtrl.dispose();
    _codeCtrl.dispose();
    super.dispose();
  }

  Future<void> _createInvite() async {
    final auth = context.read<AuthProvider>();
    setState(() => _busyCreate = true);
    try {
      // 1) Genera par X25519 y guarda la PRIV por chat
      final keys = await EncryptionService.generateX25519KeyPair();
      final myPriv = keys['priv']!;
      final myPub = keys['pub']!;
      _myPrivB64 = myPriv;

      // 2) Crea invitación pasando la pubkey
      final map = await ApiService.createInvite(
        token: auth.token!,
        isGroup: _group,
        name: _group ? (_nameCtrl.text.trim().isEmpty ? null : _nameCtrl.text.trim()) : null,
        creatorPubKeyB64: myPub,
        ttlMinutes: 15,
      );

      // 3) Guarda privada temporal bajo chatId
      final chatId = map['chat_id'] as int;
      await EncryptionService.saveChatPriv(chatId, myPriv);

      setState(() {
        _chatId = chatId;
        _code = map['code'] as String?;
        _uri = map['uri'] as String?;
        _expires = map['expires_at'] as String?;
      });
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      if (mounted) setState(() => _busyCreate = false);
    }
  }

  Future<void> _redeem() async {
    final auth = context.read<AuthProvider>();
    setState(() => _busyJoin = true);
    try {
      final code = _codeCtrl.text.trim();
      if (code.isEmpty) throw Exception('Código vacío');

      // 1) Genera par X25519 del canjeador
      final keys = await EncryptionService.generateX25519KeyPair();
      final myPriv = keys['priv']!;
      final myPub = keys['pub']!;

      // 2) Canjea invitación enviando tu pubkey; recibe chat_id + pubkey del otro
      final resp = await ApiService.redeemInvite(
        token: auth.token!,
        code: code,
        redeemerPubKeyB64: myPub,
      );
      final chatId = resp['chat_id'] as int;
      final otherPub = resp['other_pubkey'] as String?;

      if (otherPub == null || otherPub.isEmpty) {
        // El creador aún no subió su pubkey (no debería pasar con el flujo actual)
        throw Exception('Pubkey remota no disponible aún. Intenta otra vez.');
      }

      // 3) Deriva clave E2E y guárdala
      final key = await EncryptionService.deriveChatKeyFromECDH(
        myPrivB64: myPriv,
        otherPubB64: otherPub,
      );
      await EncryptionService.setChatKey(chatId, key);

      // 4) (opcional) elimina tu privada temporal si la hubieras guardado
      await EncryptionService.deleteChatPriv(chatId);

      if (!mounted) return;
      Navigator.of(context).pop<int>(chatId); // Vuelve a la lista con el chat listo
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('No se pudo canjear: $e')));
    } finally {
      if (mounted) setState(() => _busyJoin = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Nuevo chat'),
        bottom: TabBar(
          controller: _tab,
          tabs: const [
            Tab(text: 'Crear invitación'),
            Tab(text: 'Unirse con código'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tab,
        children: [
          // ===== Crear invitación =====
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('Chat de grupo'),
                  value: _group,
                  onChanged: (v) => setState(() => _group = v),
                ),
                if (_group)
                  TextField(
                    controller: _nameCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Nombre del grupo (opcional)',
                    ),
                  ),
                const SizedBox(height: 12),
                FilledButton.icon(
                  onPressed: _busyCreate ? null : _createInvite,
                  icon: _busyCreate
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.qr_code_2),
                  label: const Text('Generar invitación'),
                ),
                const SizedBox(height: 16),
                if (_code != null) ...[
                  SelectableText('Código: $_code', style: const TextStyle(fontFamily: 'monospace')),
                  const SizedBox(height: 8),
                  if (_uri != null)
                    Container(
                      decoration: BoxDecoration(
                        color: cs.surfaceVariant,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      padding: const EdgeInsets.all(12),
                      child: QrImageView(
                        data: _uri!,
                        size: 180,
                        version: QrVersions.auto,
                      ),
                    ),
                  const SizedBox(height: 8),
                  if (_expires != null)
                    Text('Expira: $_expires', style: TextStyle(color: cs.secondary)),
                ],
              ],
            ),
          ),
          // ===== Unirse con código =====
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                TextField(
                  controller: _codeCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Pega el código',
                  ),
                ),
                const SizedBox(height: 12),
                FilledButton.icon(
                  onPressed: _busyJoin ? null : _redeem,
                  icon: _busyJoin
                      ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.login),
                  label: const Text('Unirse'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
