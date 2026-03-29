# modules/file_protect.py

import os
import subprocess
import platform

def proteger_archivo_extremo(path):
    try:
        if os.name == "nt":
            # Windows: Atributos +h +s +r y permisos NTFS extremos
            os.system(f'attrib +h +s +r "{path}"')
            try:
                import win32security, ntsecuritycon
                user, domain, type = win32security.LookupAccountName("", os.getlogin())
                sd = win32security.GetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION)
                dacl = win32security.ACL()
                # Solo el usuario propietario puede borrar
                dacl.AddAccessAllowedAce(win32security.ACL_REVISION, ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE, user)
                sd.SetSecurityDescriptorDacl(1, dacl, 0)
                win32security.SetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION, sd)
            except Exception:
                pass
        else:
            # Linux: Inmutable + permisos 000
            os.chmod(path, 0o000)
            subprocess.run(["chattr", "+i", path], stderr=subprocess.DEVNULL)
    except Exception:
        pass

def quitar_proteccion(path):
    try:
        if os.name == "nt":
            os.system(f'attrib -h -s -r "{path}"')
        else:
            subprocess.run(["chattr", "-i", path], stderr=subprocess.DEVNULL)
            os.chmod(path, 0o700)
    except Exception:
        pass
