from flask import Flask, render_template, session, redirect, url_for, flash, request, send_file
from flask_mysqldb import MySQL
from datetime import datetime
from werkzeug.utils import secure_filename
import bcrypt
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "concesionario"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# Configuración para subida de archivos
UPLOAD_FOLDER = 'static/Media'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB máximo

# Crear carpeta de Media si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

mysql = MySQL(app)

app.secret_key = "clave123"  # Cambiar esto después


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Función para conectar a la base de datos de vehículos
def get_vehiculos_connection():
    import MySQLdb
    return MySQLdb.connect(
        host="localhost",
        user="root",
        password="",
        db="concesionario",
        cursorclass=MySQLdb.cursors.DictCursor
    )


# Ruta principal
@app.route("/")
def index():
    profile_image = None
    if "username" in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT profile_image FROM users WHERE username = %s", (session["username"],))
        user = cur.fetchone()
        cur.close()
        if user and user.get('profile_image'):
            profile_image = user['profile_image']
    
    return render_template("index.html", profile_image=profile_image)


# EL DASHBOARD - MODIFICADO PARA MANEJAR POST
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" not in session:
        flash("Debes iniciar sesión para acceder al panel.", "warning")
        return redirect(url_for("login"))
    
    # Obtener datos del usuario
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (session["username"],))
    user = cur.fetchone()
    cur.close()
    
    if not user:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("logout"))
    
    # Manejar la subida de imagen
    if request.method == "POST":
        if 'profile_image' not in request.files:
            flash("No se seleccionó ningún archivo.", "warning")
            return redirect(url_for("dashboard"))
        
        file = request.files['profile_image']
        
        if file.filename == '':
            flash("No se seleccionó ningún archivo.", "warning")
            return redirect(url_for("dashboard"))
        
        if file and allowed_file(file.filename):
            # Generar nombre seguro para el archivo
            filename = secure_filename(file.filename)
            # Agregar username al nombre para hacerlo único
            name, ext = os.path.splitext(filename)
            filename = f"{session['username']}_{name}{ext}"
            
            filepath = os.path.join('static/uploads', filename)
            file.save(filepath)
            
            # Actualizar la base de datos
            relative_path = f"uploads/{filename}"
            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE users SET profile_image = %s WHERE username = %s",
                (relative_path, session["username"])
            )
            mysql.connection.commit()
            cur.close()
            
            flash("Imagen de perfil actualizada correctamente.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Formato de archivo no permitido. Use JPG, JPEG, PNG o GIF.", "danger")
            return redirect(url_for("dashboard"))
    
    # GET - Mostrar el dashboard
    now = datetime.now()
    profile_image = user.get('profile_image', 'uploads/default_avatar.png')
    phone = user.get('phone', 'No especificado')
    user_type = user.get('user_type', 'client')
    
    return render_template(
        "dashboard.html", 
        username=session["username"], 
        now=now,
        profile_image=profile_image,
        phone=phone,
        user_type=user_type
    )


# ruta de modo oscuro
@app.route("/toggle-dark-mode", methods=["POST"])
def toggle_dark_mode():
    if "username" not in session:
        return redirect(url_for("login"))
    
    # Cambiar el estado del modo oscuro en la sesión
    current_mode = session.get('dark_mode', False)
    session['dark_mode'] = not current_mode
    
    return redirect(request.referrer or url_for('dashboard'))


# Flota
@app.route("/flota")
def flota():
    profile_image = None
    
    # Obtener foto de perfil de user_auth
    if "username" in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT profile_image FROM users WHERE username = %s", (session["username"],))
        user = cur.fetchone()
        cur.close()
        if user and user.get('profile_image'):
            profile_image = user['profile_image']
    
    # Obtener vehículos de la base de datos vehiculos
    conn_vehiculos = get_vehiculos_connection()
    cur_vehiculos = conn_vehiculos.cursor()
    cur_vehiculos.execute("SELECT * FROM vehiculos ORDER BY destacado DESC, nombre ASC")
    vehiculos = cur_vehiculos.fetchall()
    cur_vehiculos.close()
    conn_vehiculos.close()
    
    return render_template("flota.html", vehiculos=vehiculos, profile_image=profile_image)


# Construccion
@app.route("/en-construccion")
def construccion():
    return render_template("construction.html")


# Guia Usuario
@app.route("/guia-usuario")
def guia_usuario():
    profile_image = None
    if "username" in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT profile_image FROM users WHERE username = %s", (session["username"],))
        user = cur.fetchone()
        cur.close()
        if user and user.get('profile_image'):
            profile_image = user['profile_image']
    
    return render_template("guia_usuario.html", profile_image=profile_image)


# Ruta de login - MEJORADA
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_input = request.form["user_input"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username = %s OR email = %s",
            (user_input, user_input)
        )
        user = cur.fetchone()
        cur.close()

        if user:
            # Verifica contraseña con bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session['username'] = user['username']
                flash("¡Bienvenido! Inicio de sesión exitoso.", "success")
                return redirect(url_for('index'))
            else:
                flash("❌ Contraseña incorrecta. Por favor, intenta nuevamente.", "danger")
                return redirect(url_for('login'))
        else:
            flash("❌ Usuario no encontrado. Verifica tus datos o regístrate.", "danger")
            return redirect(url_for('login'))

    return render_template("login.html")


# Ruta de logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("Sesión cerrada con éxito.", "info")
    return redirect(url_for("index"))


# Ruta de register - ACTUALIZADA
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        user_type = request.form.get("user_type", "client")  # Por defecto 'client'

        # Encriptar contraseña con bcrypt
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        try:
            # Insertar en la tabla users
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO users (username, email, phone, password, user_type) VALUES (%s, %s, %s, %s, %s)",
                (username, email, phone, hashed_pw, user_type)
            )
            mysql.connection.commit()
            cur.close()

            # CAMBIO AQUÍ: Redirigir a página de éxito
            return render_template("registro_exitoso.html", username=username)
        except Exception as e:
            flash(f"Error al registrar usuario: {str(e)}", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


# Nueva ruta para la página de registro exitoso
@app.route("/registro-exitoso")
def registro_exitoso():
    # Esta ruta es opcional, ya que render_template se puede llamar directamente
    return render_template("registro_exitoso.html", username="Usuario")


# Actualizar la ruta del panel de administración
@app.route("/admin-panel", methods=["GET", "POST"])
def admin_panel():
    # Verificar que sea administrador
    if "username" not in session:
        flash("Debes iniciar sesión para acceder.", "danger")
        return redirect(url_for("login"))
    
    # Verificar tipo de usuario
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_type FROM users WHERE username = %s", (session["username"],))
    user = cur.fetchone()
    cur.close()
    
    if not user or user.get('user_type') != 'admin':
        flash("No tienes permisos para acceder a esta página.", "danger")
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        form_type = request.form.get("form_type")
        
        # ===== AGREGAR VEHÍCULO =====
        if form_type == "vehiculo":
            nombre = request.form["nombre"]
            categoria = request.form["categoria"]
            capacidad_personas = request.form["capacidad_personas"]
            capacidad_maletas = request.form["capacidad_maletas"]
            transmision = request.form["transmision"]
            aire_acondicionado = 1 if request.form.get("aire_acondicionado") else 0
            precio = request.form["precio"]
            descuento_soat = request.form.get("descuento_soat", None)
            if descuento_soat == "":
                descuento_soat = None
            descripcion = request.form["descripcion"]
            destacado = 1 if request.form.get("destacado") else 0
            
            # Manejar la imagen
            if 'imagen' not in request.files:
                flash("No se seleccionó ninguna imagen.", "danger")
                return redirect(url_for("admin_panel"))
            
            file = request.files['imagen']
            
            if file.filename == '':
                flash("No se seleccionó ninguna imagen.", "danger")
                return redirect(url_for("admin_panel"))
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                imagen_path = f"Media/{filename}"
                
                try:
                    conn_vehiculos = get_vehiculos_connection()
                    cur_vehiculos = conn_vehiculos.cursor()
                    
                    cur_vehiculos.execute(
                        """INSERT INTO vehiculos 
                        (nombre, categoria, capacidad_personas, capacidad_maletas, transmision, 
                        aire_acondicionado, precio, descuento_soat, descripcion, imagen, destacado) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (nombre, categoria, capacidad_personas, capacidad_maletas, transmision,
                         aire_acondicionado, precio, descuento_soat, descripcion, imagen_path, destacado)
                    )
                    
                    conn_vehiculos.commit()
                    cur_vehiculos.close()
                    conn_vehiculos.close()
                    
                    flash(f"✅ Vehículo '{nombre}' agregado exitosamente.", "success")
                    return redirect(url_for("admin_panel"))
                except Exception as e:
                    flash(f"Error al agregar vehículo: {str(e)}", "danger")
                    return redirect(url_for("admin_panel"))
            else:
                flash("Formato de archivo no permitido. Use JPG, JPEG, PNG, GIF o WEBP.", "danger")
                return redirect(url_for("admin_panel"))
        
        # ===== AGREGAR USUARIO =====
        elif form_type == "usuario":
            username = request.form["username"]
            email = request.form["email"]
            phone = request.form["phone"]
            password = request.form["password"]
            user_type = request.form["user_type"]
            
            # Encriptar contraseña
            hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            
            try:
                cur = mysql.connection.cursor()
                cur.execute(
                    "INSERT INTO users (username, email, phone, password, user_type) VALUES (%s, %s, %s, %s, %s)",
                    (username, email, phone, hashed_pw, user_type)
                )
                mysql.connection.commit()
                cur.close()
                
                flash(f"✅ Usuario '{username}' agregado exitosamente.", "success")
                return redirect(url_for("admin_panel"))
            except Exception as e:
                flash(f"Error al agregar usuario: {str(e)}", "danger")
                return redirect(url_for("admin_panel"))
    
    # GET - Mostrar el panel con datos
    # Obtener vehículos
    conn_vehiculos = get_vehiculos_connection()
    cur_vehiculos = conn_vehiculos.cursor()
    cur_vehiculos.execute("SELECT * FROM vehiculos ORDER BY created_at DESC")
    vehiculos = cur_vehiculos.fetchall()
    cur_vehiculos.close()
    conn_vehiculos.close()
    
    # Obtener usuarios
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users ORDER BY created_at DESC")
    usuarios = cur.fetchall()

    # Contar tipos de usuarios
    cur.execute("SELECT COUNT(*) as count FROM users WHERE user_type = 'admin'")
    admins_count = cur.fetchone()['count']
    
    cur.execute("SELECT COUNT(*) as count FROM users WHERE user_type = 'client'")
    clients_count = cur.fetchone()['count']
    
    cur.close()
    
    return render_template("admin_panel.html", 
                         vehiculos=vehiculos, 
                         usuarios=usuarios,
                         admins_count=admins_count,
                         clients_count=clients_count)


# ===== NUEVA RUTA: EDITAR VEHÍCULO =====
@app.route("/edit-vehiculo/<int:id>", methods=["GET", "POST"])
def edit_vehiculo(id):
    # Verificar que sea administrador
    if "username" not in session:
        flash("Debes iniciar sesión.", "danger")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_type FROM users WHERE username = %s", (session["username"],))
    user = cur.fetchone()
    cur.close()
    
    if not user or user.get('user_type') != 'admin':
        flash("No tienes permisos.", "danger")
        return redirect(url_for("dashboard"))
    
    conn_vehiculos = get_vehiculos_connection()
    cur_vehiculos = conn_vehiculos.cursor()
    
    if request.method == "POST":
        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        capacidad_personas = request.form["capacidad_personas"]
        capacidad_maletas = request.form["capacidad_maletas"]
        transmision = request.form["transmision"]
        aire_acondicionado = 1 if request.form.get("aire_acondicionado") else 0
        precio = request.form["precio"]
        descuento_soat = request.form.get("descuento_soat", None)
        if descuento_soat == "":
            descuento_soat = None
        descripcion = request.form["descripcion"]
        destacado = 1 if request.form.get("destacado") else 0
        
        # Verificar si hay nueva imagen
        if 'imagen' in request.files and request.files['imagen'].filename != '':
            file = request.files['imagen']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                imagen_path = f"Media/{filename}"
                
                cur_vehiculos.execute(
                    """UPDATE vehiculos SET nombre=%s, categoria=%s, capacidad_personas=%s, 
                    capacidad_maletas=%s, transmision=%s, aire_acondicionado=%s, precio=%s, 
                    descuento_soat=%s, descripcion=%s, imagen=%s, destacado=%s WHERE id=%s""",
                    (nombre, categoria, capacidad_personas, capacidad_maletas, transmision,
                     aire_acondicionado, precio, descuento_soat, descripcion, imagen_path, destacado, id)
                )
            else:
                flash("Formato de archivo no permitido.", "danger")
                return redirect(url_for("edit_vehiculo", id=id))
        else:
            # Sin cambio de imagen
            cur_vehiculos.execute(
                """UPDATE vehiculos SET nombre=%s, categoria=%s, capacidad_personas=%s, 
                capacidad_maletas=%s, transmision=%s, aire_acondicionado=%s, precio=%s, 
                descuento_soat=%s, descripcion=%s, destacado=%s WHERE id=%s""",
                (nombre, categoria, capacidad_personas, capacidad_maletas, transmision,
                 aire_acondicionado, precio, descuento_soat, descripcion, destacado, id)
            )
        
        conn_vehiculos.commit()
        cur_vehiculos.close()
        conn_vehiculos.close()
        
        flash(f"✅ Vehículo '{nombre}' actualizado exitosamente.", "success")
        return redirect(url_for("admin_panel"))
    
    # GET - Obtener datos del vehículo
    cur_vehiculos.execute("SELECT * FROM vehiculos WHERE id = %s", (id,))
    vehiculo = cur_vehiculos.fetchone()
    cur_vehiculos.close()
    conn_vehiculos.close()
    
    if not vehiculo:
        flash("Vehículo no encontrado.", "danger")
        return redirect(url_for("admin_panel"))
    
    return render_template("edit_vehiculo.html", vehiculo=vehiculo)


# ===== NUEVA RUTA: EDITAR USUARIO =====
@app.route("/edit-usuario/<int:id>", methods=["GET", "POST"])
def edit_usuario(id):
    # Verificar que sea administrador
    if "username" not in session:
        flash("Debes iniciar sesión.", "danger")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_type FROM users WHERE username = %s", (session["username"],))
    user = cur.fetchone()
    
    if not user or user.get('user_type') != 'admin':
        flash("No tienes permisos.", "danger")
        cur.close()
        return redirect(url_for("dashboard"))
    
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        user_type = request.form["user_type"]
        new_password = request.form.get("new_password", "")
        
        if new_password:
            # Si hay nueva contraseña, encriptarla
            hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            cur.execute(
                "UPDATE users SET username=%s, email=%s, phone=%s, user_type=%s, password=%s WHERE id=%s",
                (username, email, phone, user_type, hashed_pw, id)
            )
        else:
            # Sin cambio de contraseña
            cur.execute(
                "UPDATE users SET username=%s, email=%s, phone=%s, user_type=%s WHERE id=%s",
                (username, email, phone, user_type, id)
            )
        
        mysql.connection.commit()
        cur.close()
        
        flash(f"✅ Usuario '{username}' actualizado exitosamente.", "success")
        return redirect(url_for("admin_panel"))
    
    # GET - Obtener datos del usuario
    cur.execute("SELECT * FROM users WHERE id = %s", (id,))
    usuario = cur.fetchone()
    cur.close()
    
    if not usuario:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("admin_panel"))
    
    return render_template("edit_usuario.html", usuario=usuario)


# Ruta para eliminar vehículo
@app.route("/delete-vehiculo/<int:id>", methods=["POST"])
def delete_vehiculo(id):
    # Verificar que sea administrador
    if "username" not in session:
        flash("Debes iniciar sesión.", "danger")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_type FROM users WHERE username = %s", (session["username"],))
    user = cur.fetchone()
    cur.close()
    
    if not user or user.get('user_type') != 'admin':
        flash("No tienes permisos.", "danger")
        return redirect(url_for("dashboard"))
    
    try:
        conn_vehiculos = get_vehiculos_connection()
        cur_vehiculos = conn_vehiculos.cursor()
        
        # Obtener info del vehículo antes de eliminarlo
        cur_vehiculos.execute("SELECT nombre, imagen FROM vehiculos WHERE id = %s", (id,))
        vehiculo = cur_vehiculos.fetchone()
        
        if vehiculo:
            # Eliminar de la base de datos
            cur_vehiculos.execute("DELETE FROM vehiculos WHERE id = %s", (id,))
            conn_vehiculos.commit()
            
            flash(f"🗑️ Vehículo '{vehiculo['nombre']}' eliminado correctamente.", "success")
        else:
            flash("Vehículo no encontrado.", "danger")
        
        cur_vehiculos.close()
        conn_vehiculos.close()
    except Exception as e:
        flash(f"Error al eliminar: {str(e)}", "danger")
    
    return redirect(url_for("admin_panel"))


# Ruta para eliminar usuario
@app.route("/delete-usuario/<int:id>", methods=["POST"])
def delete_usuario(id):
    # Verificar que sea administrador
    if "username" not in session:
        flash("Debes iniciar sesión.", "danger")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_type FROM users WHERE username = %s", (session["username"],))
    user = cur.fetchone()
    
    if not user or user.get('user_type') != 'admin':
        flash("No tienes permisos.", "danger")
        cur.close()
        return redirect(url_for("dashboard"))
    
    # Verificar que no se esté eliminando a sí mismo
    cur.execute("SELECT username FROM users WHERE id = %s", (id,))
    usuario_eliminar = cur.fetchone()
    
    if usuario_eliminar and usuario_eliminar['username'] == session['username']:
        flash("⚠️ No puedes eliminar tu propia cuenta.", "danger")
        cur.close()
        return redirect(url_for("admin_panel"))
    
    try:
        # Obtener nombre antes de eliminar
        cur.execute("SELECT username FROM users WHERE id = %s", (id,))
        usuario = cur.fetchone()
        
        if usuario:
            # Eliminar usuario
            cur.execute("DELETE FROM users WHERE id = %s", (id,))
            mysql.connection.commit()
            
            flash(f"🗑️ Usuario '{usuario['username']}' eliminado correctamente.", "success")
        else:
            flash("Usuario no encontrado.", "danger")
        
        cur.close()
    except Exception as e:
        flash(f"Error al eliminar usuario: {str(e)}", "danger")
    
    return redirect(url_for("admin_panel"))


# ===== NUEVA RUTA: GENERAR PDF DE VEHÍCULOS =====
@app.route("/generar-pdf-vehiculos")
def generar_pdf_vehiculos():
    if "username" not in session:
        flash("Debes iniciar sesión.", "danger")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_type FROM users WHERE username = %s", (session["username"],))
    user = cur.fetchone()
    cur.close()
    
    if not user or user.get('user_type') != 'admin':
        flash("No tienes permisos.", "danger")
        return redirect(url_for("dashboard"))
    
    # Obtener vehículos más recientes
    conn_vehiculos = get_vehiculos_connection()
    cur_vehiculos = conn_vehiculos.cursor()
    cur_vehiculos.execute("SELECT * FROM vehiculos ORDER BY created_at DESC LIMIT 10")
    vehiculos = cur_vehiculos.fetchall()
    cur_vehiculos.close()
    conn_vehiculos.close()
    
    # Crear PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elementos = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#004e92'),
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    # Título
    titulo = Paragraph("Informe de Vehículos Registrados", title_style)
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))
    
    # Fecha
    fecha = Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
    elementos.append(fecha)
    elementos.append(Spacer(1, 20))
    
    # Tabla de vehículos
    data = [['Nombre', 'Categoría', 'Precio', 'Personas', 'Fecha Registro']]
    
    for v in vehiculos:
        data.append([
            v['nombre'],
            v['categoria'],
            f"${v['precio']:,.0f}",
            str(v['capacidad_personas']),
            v['created_at'].strftime('%d/%m/%Y')
        ])
    
    tabla = Table(data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 0.8*inch, 1.2*inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004e92')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    elementos.append(tabla)
    elementos.append(Spacer(1, 20))
    
    # Resumen
    total = len(vehiculos)
    resumen = Paragraph(f"<b>Total de vehículos en el informe:</b> {total}", styles['Normal'])
    elementos.append(resumen)
    
    # Construir PDF
    doc.build(elementos)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'informe_vehiculos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
        mimetype='application/pdf'
    )


# ===== NUEVA RUTA: GENERAR PDF DE USUARIOS =====
@app.route("/generar-pdf-usuarios")
def generar_pdf_usuarios():
    if "username" not in session:
        flash("Debes iniciar sesión.", "danger")
        return redirect(url_for("login"))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_type FROM users WHERE username = %s", (session["username"],))
    user = cur.fetchone()
    
    if not user or user.get('user_type') != 'admin':
        flash("No tienes permisos.", "danger")
        cur.close()
        return redirect(url_for("dashboard"))
    
    # Obtener usuarios más recientes
    cur.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT 10")
    usuarios = cur.fetchall()
    cur.close()
    
    # Crear PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elementos = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#004e92'),
        spaceAfter=30,
        alignment=1
    )
    
    # Título
    titulo = Paragraph("Informe de Usuarios Registrados", title_style)
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))
    
    # Fecha
    fecha = Paragraph(f"<b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
    elementos.append(fecha)
    elementos.append(Spacer(1, 20))
    
    # Tabla de usuarios
    data = [['Usuario', 'Email', 'Teléfono', 'Tipo', 'Fecha Registro']]
    
    for u in usuarios:
        tipo = 'Admin' if u['user_type'] == 'admin' else 'Cliente'
        data.append([
            u['username'],
            u['email'],
            u['phone'],
            tipo,
            u['created_at'].strftime('%d/%m/%Y')
        ])
    
    tabla = Table(data, colWidths=[1.5*inch, 2*inch, 1.3*inch, 0.9*inch, 1.2*inch])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004e92')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    
    elementos.append(tabla)
    elementos.append(Spacer(1, 20))
    
    # Resumen
    total = len(usuarios)
    resumen = Paragraph(f"<b>Total de usuarios en el informe:</b> {total}", styles['Normal'])
    elementos.append(resumen)
    
    # Construir PDF
    doc.build(elementos)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'informe_usuarios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
        mimetype='application/pdf'
    )


# ====== ESTO VA AL FINAL ======
if __name__ == "__main__":
    app.run(debug=True)