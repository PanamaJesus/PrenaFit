from django.core.mail import send_mail
from django.conf import settings

def enviar_alerta_emergencia(usuario, contacto_emergencia):
    """
    Envía un correo de alerta al contacto de emergencia.
    """
    destinatarios = [contacto_emergencia.correo] 

    asunto = f"🔴 ALERTA CRÍTICA de PrenaFit - {usuario.nombre} {usuario.ap_pat}"
    
    # 📌 ¡CAMBIA ESTAS LÍNEAS!
    mensaje_texto = (
        f"ALERTA CRÍTICA: La usuaria {usuario.nombre} {usuario.ap_pat} ha activado el botón de emergencia.\n\n"
        f"Detalles del contacto registrado:\n"
        f" - Nombre del contacto: {contacto_emergencia.nombre} {contacto_emergencia.ap_pat}\n" # <--- CORREGIDO
        f" - Correo del usuario: {usuario.correo}\n\n"
        f"Por favor, comuníquese inmediatamente con el usuario. Si la ubicación GPS está disponible, búsquela en el registro de alertas."
    )
    
    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios,
            fail_silently=False, 
        )
        return True
    
    except Exception as e:
        # Aquí verás el error de conexión SMTP si todavía persiste algo
        print(f"❌ ERROR al enviar correo a {contacto_emergencia.correo}: {e}")
        return False