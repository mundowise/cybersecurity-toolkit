import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../models/chat.dart';
import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import 'chat_screen.dart';
import 'new_chat_screen.dart';

class ChatListScreen extends StatefulWidget {
  const ChatListScreen({super.key});

  @override
  State<ChatListScreen> createState() => _ChatListScreenState();
}

class _ChatListScreenState extends State<ChatListScreen> {
  bool _loading = true;
  List<Chat> _chats = const [];

  @override
  void initState() {
    super.initState();
    _loadChats();
  }

  Future<void> _loadChats() async {
    try {
      final auth = context.read<AuthProvider>();
      final list = await ApiService.getChats(auth.token!);
      setState(() {
        _chats = list;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error cargando chats: $e')),
      );
    }
  }

  Future<void> _openNewChat() async {
    // Abre pantalla de invitación/unirse; si retorna chatId, navega directo a ese chat
    final chatId = await Navigator.of(context).push<int>(
      MaterialPageRoute(builder: (_) => const NewChatScreen()),
    );
    if (chatId != null) {
      await _loadChats();
      final chat = _chats.where((c) => c.id == chatId).cast<Chat?>().firstWhere(
            (c) => c != null,
            orElse: () => null,
          );
      if (!mounted) return;
      if (chat != null) {
        Navigator.of(context).push(
          MaterialPageRoute(builder: (_) => ChatScreen(chat: chat)),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Chats'),
        actions: [
          IconButton(
            tooltip: 'Nuevo chat',
            icon: const Icon(Icons.add_link),
            onPressed: _openNewChat,
          ),
          IconButton(
            tooltip: 'Refrescar',
            icon: const Icon(Icons.refresh),
            onPressed: _loadChats,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _openNewChat,
        icon: const Icon(Icons.qr_code_2),
        label: const Text('Nuevo chat'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadChats,
              child: _chats.isEmpty
                  ? ListView(
                      children: [
                        const SizedBox(height: 80),
                        Center(
                          child: Text(
                            'Sin chats. Crea una invitación para empezar.',
                            style: TextStyle(color: cs.secondary),
                          ),
                        ),
                      ],
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      itemCount: _chats.length,
                      separatorBuilder: (_, __) => const Divider(height: 1),
                      itemBuilder: (ctx, i) {
                        final c = _chats[i];
                        final title = c.name ?? (c.isGroup ? 'Grupo' : 'Chat');
                        return ListTile(
                          title: Text(title),
                          leading: CircleAvatar(
                            child: Text(c.isGroup ? 'G' : '1:1'),
                          ),
                          trailing: const Icon(Icons.chevron_right),
                          onTap: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(builder: (_) => ChatScreen(chat: c)),
                            );
                          },
                        );
                      },
                    ),
            ),
    );
  }
}
