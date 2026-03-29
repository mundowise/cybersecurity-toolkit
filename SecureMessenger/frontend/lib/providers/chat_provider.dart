import 'package:flutter/material.dart';
import '../models/chat.dart';
import '../services/api_service.dart';
import '../models/message.dart';

class ChatProvider extends ChangeNotifier {
  List<Chat> _chats = [];
  List<Chat> get chats => _chats;

  Future<void> loadChats(String token) async {
    _chats = await ApiService.getChats(token);
    notifyListeners();
  }

  Future<Chat> createChat(String token, List<int> memberIds, {bool isGroup = false, String? name}) async {
    final chat = await ApiService.createChat(token, memberIds, isGroup: isGroup, name: name);
    _chats.add(chat);
    notifyListeners();
    return chat;
  }

   final Map<int, List<Message>> _messages = {};
  Map<int, List<Message>> get messages => _messages;

  Future<void> loadMessages(String token, int chatId) async {
    final msgs = await ApiService.getMessages(token, chatId);
    _messages[chatId] = msgs;
    notifyListeners();
  }

  Future<void> sendMessage(String token, int chatId, Message message) async {
    final msg = await ApiService.sendMessage(token, message);
    _messages.putIfAbsent(chatId, () => []).add(msg);
    notifyListeners();
  }
}