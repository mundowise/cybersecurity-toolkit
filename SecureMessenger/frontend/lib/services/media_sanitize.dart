// lib/services/media_sanitize.dart
import 'dart:io';
import 'package:image/image.dart' as img;

class MediaSanitize {
  static Future<File> stripImageMetadata(File input, String outPath) async {
    final bytes = await input.readAsBytes();
    final im = img.decodeImage(bytes);
    if (im == null) throw Exception('Imagen inválida');
    final outBytes = img.encodeJpg(im, quality: 92); // re-encode sin EXIF
    final out = File(outPath);
    await out.writeAsBytes(outBytes, flush: true);
    return out;
  }
}
