import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../services/api_service.dart';

class AuthProvider with ChangeNotifier {
  // La seguimos usando para otras cosas si hiciera falta (p.ej. limpiar todo)
  final _storage = const FlutterSecureStorage();

  String? _token;
  int? _userId;
  String? _alias;

  String? get token => _token;
  int? get userId => _userId;
  String? get alias => _alias;

  bool get isLoggedIn => _token != null && _token!.isNotEmpty;

  // Ahora NO cargamos sesión de disco: siempre arranca deslogueado
  Future<void> loadSession() async {
    _token = null;
    _userId = null;
    _alias = null;
    notifyListeners();
  }

  Future<void> register(String alias, String password) async {
    await ApiService.register(alias, password);
    await login(alias, password);
  }

  Future<void> login(String alias, String password) async {
    final res = await ApiService.login(alias, password);
    _token = res['access_token'] as String?;
    final user = res['user'] as Map<String, dynamic>?;
    _userId = (user != null && user['id'] is int)
        ? user['id'] as int
        : int.tryParse('${user?["id"]}');
    _alias = user?['alias']?.toString();

    // IMPORTANTE: NO guardamos nada en disco -> sesión solo en memoria
    // Si quieres además limpiar restos de sesiones anteriores:
    await _storage.delete(key: 'token');
    await _storage.delete(key: 'user_id');
    await _storage.delete(key: 'alias');

    notifyListeners();
  }

  Future<void> logout({bool wipeAllSecureStorage = false}) async {
    _token = null;
    _userId = null;
    _alias = null;

    // Limpia posibles claves antiguas de sesión
    await _storage.delete(key: 'token');
    await _storage.delete(key: 'user_id');
    await _storage.delete(key: 'alias');

    // Si quieres máxima privacidad, borra TODO el secure storage,
    // lo cual también eliminaría las claves simétricas de chats guardadas por EncryptionService.
    if (wipeAllSecureStorage) {
      await _storage.deleteAll();
    }
    notifyListeners();
  }
}
