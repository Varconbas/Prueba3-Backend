// --- BASE DE DATOS SIMULADA ---
let productos = [
    { id: 1, nombre: "Shampoo Revitalizante", descripcion: "Fórmula suave con extractos naturales que hidrata y restaura el brillo.", precio: 15000, stock: 5, imagen: "https://placehold.co/400x500/d8b4e2/4a3b4c?text=Shampoo+Spa" },
    { id: 2, nombre: "Aceite de Argán Premium", descripcion: "Sérum concentrado para puntas partidas. Aporta suavidad extrema.", precio: 22000, stock: 3, imagen: "https://placehold.co/400x500/f8c8d4/4a3b4c?text=Aceite+Argan" },
    { id: 3, nombre: "Mascarilla Capilar Oro", descripcion: "Tratamiento intensivo con micropartículas doradas para nutrición profunda.", precio: 18500, stock: 0, imagen: "https://placehold.co/400x500/f3e1f0/4a3b4c?text=Mascarilla" }
];

let servicios = [
    { id: 1, nombre: "Peluquería y Perfilado", precio: 18000, duracion: "45 min" },
    { id: 2, nombre: "Spa Capilar Nutritivo", precio: 25000, duracion: "60 min" },
    { id: 3, nombre: "Masaje Descontracturante", precio: 30000, duracion: "50 min" },
    { id: 4, nombre: "Tinaja Relajante", precio: 40000, duracion: "90 min" }
];

let carrito = [];
let citasAgendadas = [];

let servicioSeleccionado = null;
let horaSeleccionada = null;

// --- NAVEGACIÓN ---
function cambiarVista(idVista, boton) {
    document.querySelectorAll('.vista').forEach(vista => vista.classList.remove('activa'));
    document.getElementById(idVista).classList.add('activa');
    
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    if(boton) boton.classList.add('active');

    if (idVista === 'tienda') renderizarTienda();
    if (idVista === 'carrito') renderizarCarrito();
    if (idVista === 'admin') renderizarAdmin();
    if (idVista === 'agendar') renderizarAgendar();
}

// --- LÓGICA DE LA TIENDA Y CARRITO ---
function renderizarTienda() {
    const contenedor = document.getElementById('contenedor-productos');
    contenedor.innerHTML = '';
    productos.forEach(prod => {
        const itemEnCarrito = carrito.find(item => item.id === prod.id);
        const cantidadEnCarrito = itemEnCarrito ? itemEnCarrito.cantidad : 0;
        const stockDisponible = prod.stock - cantidadEnCarrito;
        const agotado = stockDisponible <= 0;

        contenedor.innerHTML += `
            <div class="tarjeta-producto ${agotado ? 'agotado' : ''}">
                <img src="${prod.imagen}" alt="${prod.nombre}" class="img-producto">
                <div class="tarjeta-body">
                    <h3>${prod.nombre}</h3>
                    <p class="desc">${prod.descripcion}</p>
                    <div class="precio-stock">
                        <span class="precio">$${prod.precio.toLocaleString('es-CL')}</span>
                        <span class="stock-badge ${agotado ? 'stock-cero' : ''}">${agotado ? 'Agotado' : `Stock: ${stockDisponible}`}</span>
                    </div>
                    <button class="btn ghost btn-carrito" onclick="agregarAlCarrito(${prod.id})" ${agotado ? 'disabled' : ''}>
                        ${agotado ? 'Sin Stock' : 'Agregar al Carrito'}
                    </button>
                </div>
            </div>
        `;
    });
}

function agregarAlCarrito(idProducto) {
    const producto = productos.find(p => p.id === idProducto);
    const itemEnCarrito = carrito.find(item => item.id === idProducto);
    const cantidadActual = itemEnCarrito ? itemEnCarrito.cantidad : 0;

    // VALIDACIÓN: Límite de stock
    if (cantidadActual >= producto.stock) {
        return alert("No hay más stock disponible de este producto.");
    }

    if (itemEnCarrito) itemEnCarrito.cantidad++;
    else carrito.push({ ...producto, cantidad: 1 });
    
    actualizarContador();
    renderizarTienda();
    alert(`"${producto.nombre}" añadido al carrito.`);
}

// NUEVA FUNCIÓN: Sumar o restar cantidades desde el carrito
function cambiarCantidadCarrito(idProducto, cambio) {
    const item = carrito.find(i => i.id === idProducto);
    if (!item) return;

    const productoBD = productos.find(p => p.id === idProducto);

    if (cambio === 1) {
        // Validar stock antes de sumar
        if (item.cantidad >= productoBD.stock) {
            return alert("Has alcanzado el límite de stock disponible para este producto.");
        }
        item.cantidad++;
    } else if (cambio === -1) {
        item.cantidad--;
        // Si llega a cero, lo eliminamos
        if (item.cantidad <= 0) {
            eliminarDelCarrito(idProducto);
            return; // Salimos de la función para no actualizar dos veces
        }
    }

    actualizarContador();
    renderizarCarrito();
    renderizarTienda(); // Para actualizar los badges de la tienda
}

function eliminarDelCarrito(idProducto) {
    carrito = carrito.filter(item => item.id !== idProducto);
    renderizarCarrito();
    actualizarContador();
    renderizarTienda();
}

function actualizarContador() {
    document.getElementById('contador-carrito').innerText = carrito.reduce((sum, item) => sum + item.cantidad, 0);
}

function renderizarCarrito() {
    const cuerpo = document.getElementById('cuerpo-carrito');
    cuerpo.innerHTML = '';
    let total = 0;

    if(carrito.length === 0) {
        cuerpo.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 2rem; color: var(--text-muted);">El carrito está vacío</td></tr>';
    } else {
        carrito.forEach(item => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;
            cuerpo.innerHTML += `
                <tr>
                    <td>${item.nombre}</td>
                    <td>$${item.precio.toLocaleString('es-CL')}</td>
                    <td>
                        <div class="qty-controls">
                            <button class="btn-qty" onclick="cambiarCantidadCarrito(${item.id}, -1)">-</button>
                            <span>${item.cantidad}</span>
                            <button class="btn-qty" onclick="cambiarCantidadCarrito(${item.id}, 1)">+</button>
                        </div>
                    </td>
                    <td>$${subtotal.toLocaleString('es-CL')}</td>
                    <td><button class="btn btn-danger btn-small" onclick="eliminarDelCarrito(${item.id})">Quitar</button></td>
                </tr>
            `;
        });
    }
    document.getElementById('total-precio').innerText = total.toLocaleString('es-CL');
}

function realizarCompra() {
    // VALIDACIÓN: Carrito vacío
    if(carrito.length === 0) return alert("Tu carrito está vacío.");
    
    carrito.forEach(itemCarrito => {
        const prodBD = productos.find(p => p.id === itemCarrito.id);
        if(prodBD) prodBD.stock -= itemCarrito.cantidad;
    });

    alert("Redirigiendo a Mercado Pago... ¡Compra confirmada!");
    carrito = [];
    actualizarContador();
    document.querySelector('.nav-btn').click(); 
}

// --- LÓGICA DE AGENDAMIENTO ---
function renderizarAgendar() {
    const selector = document.getElementById('selector-servicio');
    selector.innerHTML = '<option value="" disabled selected>Elige un servicio...</option>';
    servicios.forEach(srv => {
        selector.innerHTML += `<option value="${srv.id}">${srv.nombre} - $${srv.precio.toLocaleString('es-CL')} (${srv.duracion})</option>`;
    });
    
    const hoy = new Date().toISOString().split('T')[0];
    document.getElementById('fecha-cita').setAttribute('min', hoy);
}

function seleccionarHora(boton, hora) {
    document.querySelectorAll('.time-slot').forEach(btn => btn.classList.remove('selected'));
    boton.classList.add('selected');
    horaSeleccionada = hora;
}

function confirmarReserva() {
    const idServicio = document.getElementById('selector-servicio').value;
    const fecha = document.getElementById('fecha-cita').value;
    const nombreCliente = document.getElementById('nombre-cliente').value;

    // VALIDACIÓN: Campos vacíos
    if (!idServicio || !fecha || !horaSeleccionada || !nombreCliente) {
        return alert("Por favor completa todos los campos: Nombre, Servicio, Fecha y Hora.");
    }

    const servicio = servicios.find(s => s.id == idServicio);
    const abono = servicio.precio * 0.30; 

    // VALIDACIÓN: Confirmación del usuario
    if (confirm(`Estás a punto de agendar: \n${servicio.nombre}\nFecha: ${fecha} a las ${horaSeleccionada}\n\nPara confirmar debes pagar un abono del 30%: $${abono.toLocaleString('es-CL')}.\n¿Ir a pagar?`)) {
        
        citasAgendadas.push({
            id: citasAgendadas.length + 1,
            cliente: nombreCliente,
            servicio: servicio.nombre,
            fecha: fecha,
            hora: horaSeleccionada,
            abonoPagado: abono
        });

        alert("¡Pago exitoso! Tu hora ha sido agendada y confirmada.");
        
        document.getElementById('nombre-cliente').value = '';
        document.getElementById('fecha-cita').value = '';
        document.querySelectorAll('.time-slot').forEach(btn => btn.classList.remove('selected'));
        horaSeleccionada = null;
        renderizarAdmin(); // Actualiza la tabla del admin en segundo plano
    }
}

// --- LÓGICA DE ADMINISTRACIÓN ---
function renderizarAdmin() {
    const cuerpoProd = document.getElementById('cuerpo-admin');
    cuerpoProd.innerHTML = '';
    productos.forEach(prod => {
        cuerpoProd.innerHTML += `
            <tr>
                <td>#${prod.id}</td>
                <td>${prod.nombre}</td>
                <td><input type="number" id="admin-precio-${prod.id}" value="${prod.precio}" style="width:100px;"></td>
                <td><input type="number" id="admin-stock-${prod.id}" value="${prod.stock}" style="width:80px;"></td>
                <td>
                    <button class="btn gold btn-small" style="margin-bottom:5px" onclick="actualizarProducto(${prod.id})">Guardar</button>
                    <button class="btn btn-danger btn-small" onclick="eliminarProductoAdmin(${prod.id})">Eliminar</button>
                </td>
            </tr>
        `;
    });

    const cuerpoCitas = document.getElementById('cuerpo-citas-admin');
    cuerpoCitas.innerHTML = '';
    if(citasAgendadas.length === 0) {
        cuerpoCitas.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 1rem; color: var(--text-muted);">No hay citas agendadas aún.</td></tr>';
    } else {
        citasAgendadas.forEach(cita => {
            cuerpoCitas.innerHTML += `
                <tr>
                    <td><strong>${cita.fecha}</strong><br>${cita.hora}</td>
                    <td>${cita.cliente}</td>
                    <td>${cita.servicio}</td>
                    <td style="color:var(--ciruela); font-weight:bold;">$${cita.abonoPagado.toLocaleString('es-CL')}</td>
                    <td><span class="stock-badge">Confirmada</span></td>
                </tr>
            `;
        });
    }
}

function agregarProducto() {
    const nombre = document.getElementById('nuevo-nombre').value.trim();
    const desc = document.getElementById('nuevo-desc').value.trim();
    const precio = parseInt(document.getElementById('nuevo-precio').value);
    const stock = parseInt(document.getElementById('nuevo-stock').value);
    let imagen = document.getElementById('nueva-imagen').value || "https://placehold.co/400x500/e8d8e0/4a3b4c?text=Nuevo+Producto";

    // VALIDACIÓN: Datos nulos, vacíos o negativos
    if (!nombre || !desc || isNaN(precio) || isNaN(stock) || precio <= 0 || stock < 0) {
        return alert("Verifica los campos. El precio debe ser mayor a 0 y el stock no puede ser negativo.");
    }

    productos.push({ id: (productos.length > 0 ? Math.max(...productos.map(p => p.id)) + 1 : 1), nombre, descripcion: desc, precio, stock, imagen });
    document.querySelectorAll('.formulario-admin input, .formulario-admin textarea').forEach(input => input.value = '');
    alert("Producto agregado."); 
    renderizarAdmin(); 
    renderizarTienda();
}

function actualizarProducto(id) {
    const p = parseInt(document.getElementById(`admin-precio-${id}`).value);
    const s = parseInt(document.getElementById(`admin-stock-${id}`).value);
    
    // VALIDACIÓN: Precios y stocks inválidos
    if (isNaN(p) || p <= 0 || isNaN(s) || s < 0) {
        return alert("Valores inválidos. Revisa el precio y el stock.");
    }
    
    const prod = productos.find(x => x.id === id);
    prod.precio = p; 
    prod.stock = s;
    alert(`Actualizado correctamente.`); 
    renderizarAdmin(); 
    renderizarTienda();
}

function eliminarProductoAdmin(id) {
    // VALIDACIÓN: Confirmación del administrador
    if(confirm(`¿Estás seguro de que deseas ELIMINAR permanentemente este producto?`)) {
        productos = productos.filter(p => p.id !== id);
        carrito = carrito.filter(c => c.id !== id);
        actualizarContador(); 
        renderizarAdmin(); 
        renderizarTienda(); 
        alert("Eliminado.");
    }
}

// --- INICIALIZACIÓN ---
window.onload = function() {
    renderizarTienda();
};