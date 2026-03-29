class Chat {
  final int id;
  final bool isGroup;
  final String? name;
  final List<int> members;

  Chat({required this.id, required this.isGroup, this.name, required this.members});

  factory Chat.fromJson(Map<String, dynamic> json) => Chat(
    id: json['id'],
    isGroup: json['is_group'],
    name: json['name'],
    members: List<int>.from(json['members']),
  );
}
