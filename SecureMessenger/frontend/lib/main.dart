import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';

import 'providers/auth_provider.dart';
import 'providers/chat_provider.dart';
import 'screens/login_screen.dart';
import 'screens/chat_list_screen.dart';

ThemeData buildTheme(Brightness b) {
  // Tema "hacker": negro, textos blancos, acentos rojos
  final base = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme(
      brightness: b,
      primary: const Color(0xFFFF1744),         // rojo intenso
      onPrimary: Colors.white,
      secondary: const Color(0xFFEF5350),       // rojo secundario
      onSecondary: Colors.white,
      error: const Color(0xFFD32F2F),
      onError: Colors.white,
      background: const Color(0xFF0B0B0C),      // negro profundo
      onBackground: Colors.white,
      surface: const Color(0xFF121214),
      onSurface: Colors.white70,
      surfaceVariant: const Color(0xFF1A1B1E),  // burbujas de otros
      onSurfaceVariant: Colors.white70,
      primaryContainer: const Color(0xFF2A0E12), // burbuja mía
      onPrimaryContainer: Colors.white,
      secondaryContainer: const Color(0xFF24090B),
      onSecondaryContainer: Colors.white70,
      outline: const Color(0xFF3A3B3E),
      outlineVariant: const Color(0xFF2A2B2E),
      shadow: Colors.black,
      scrim: Colors.black,
      inverseSurface: Colors.white,
      onInverseSurface: Colors.black,
      inversePrimary: const Color(0xFFFF8A80),
      tertiary: const Color(0xFFB71C1C),
      onTertiary: Colors.white,
    ),
    textTheme: GoogleFonts.interTextTheme(
      ThemeData.dark().textTheme,
    ).apply(
      bodyColor: Colors.white.withOpacity(0.90),
      displayColor: Colors.white,
    ),
    iconTheme: const IconThemeData(color: Colors.white70),
  );

  return base.copyWith(
    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF0B0B0C),
      foregroundColor: Colors.white,
    ),
    inputDecorationTheme: const InputDecorationTheme(
      filled: true,
      fillColor: Color(0xFF141417),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.all(Radius.circular(14)),
        borderSide: BorderSide(color: Color(0xFF2A2B2E)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.all(Radius.circular(14)),
        borderSide: BorderSide(color: Color(0xFF2A2B2E)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.all(Radius.circular(14)),
        borderSide: BorderSide(color: Color(0xFFFF1744)),
      ),
    ),
    cardTheme: const CardThemeData(
      margin: EdgeInsets.all(8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.all(Radius.circular(16)),
      ),
      elevation: 0,
      color: Color(0xFF121214),
    ),
  );
}

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ChatProvider()),
      ],
      child: const SecureMessengerApp(),
    ),
  );
}

class SecureMessengerApp extends StatelessWidget {
  const SecureMessengerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SecureMessenger',
      theme: buildTheme(Brightness.dark), // fuerza dark
      darkTheme: buildTheme(Brightness.dark),
      themeMode: ThemeMode.dark,
      home: const _Bootstrap(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class _Bootstrap extends StatefulWidget {
  const _Bootstrap({super.key});

  @override
  State<_Bootstrap> createState() => _BootstrapState();
}

class _BootstrapState extends State<_Bootstrap> {
  late Future<void> _load;

  @override
  void initState() {
    super.initState();
    _load = context.read<AuthProvider>().loadSession();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<void>(
      future: _load,
      builder: (context, snap) {
        if (snap.connectionState != ConnectionState.done) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        final isLogged = context.read<AuthProvider>().isLoggedIn;
        if (isLogged) {
          return const ChatListScreen();
        }
        return const LoginScreen();
      },
    );
  }
}
