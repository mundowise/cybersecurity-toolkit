class Message {
  final int id;
  final int chatId;
  final int senderId;
  final String content;
  final String sentAt;          // ISO8601 o timestamp del server
  final String? expiresAt;      // ISO8601 o null
  final String type;            // 'text' | 'file' | 'voice' | 'system'
  final String? filename;
  final String? mimetype;

  Message({
    required this.id,
    required this.chatId,
    required this.senderId,
    required this.content,
    required this.sentAt,
    required this.expiresAt,
    required this.type,
    required this.filename,
    required this.mimetype,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'] ?? 0,
      chatId: json['chat_id'] ?? json['chatId'] ?? 0,
      senderId: json['sender_id'] ?? json['senderId'] ?? 0,
      content: (json['content'] ?? '').toString(),
      sentAt: (json['created_at'] ?? json['sent_at'] ?? '').toString(),
      expiresAt: json['expires_at']?.toString(),
      type: (json['type'] ?? 'text').toString(),
      filename: json['filename']?.toString(),
      mimetype: json['mimetype']?.toString(),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'chat_id': chatId,
        'sender_id': senderId,
        'content': content,
        'sent_at': sentAt,
        'expires_at': expiresAt,
        'type': type,
        'filename': filename,
        'mimetype': mimetype,
      };

  Message copyWith({
    int? id,
    int? chatId,
    int? senderId,
    String? content,
    String? sentAt,
    String? expiresAt,
    String? type,
    String? filename,
    String? mimetype,
  }) {
    return Message(
      id: id ?? this.id,
      chatId: chatId ?? this.chatId,
      senderId: senderId ?? this.senderId,
      content: content ?? this.content,
      sentAt: sentAt ?? this.sentAt,
      expiresAt: expiresAt ?? this.expiresAt,
      type: type ?? this.type,
      filename: filename ?? this.filename,
      mimetype: mimetype ?? this.mimetype,
    );
  }
}
