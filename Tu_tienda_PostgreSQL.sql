-- Tabla Cliente
CREATE TABLE "Cliente" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    telefono VARCHAR(20),
    fecha_nacimiento DATE,
    tipo_documento VARCHAR(20) DEFAULT 'CC',
    numero_documento VARCHAR(50) DEFAULT 'Sin número',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    imagen_perfil VARCHAR(255) DEFAULT 'default/Defaul.jpg'
);

-- Tabla Tienda
CREATE TABLE "Tienda" (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    horarios TEXT,
    telefono VARCHAR(20),
    descripcion TEXT,
    logo_url VARCHAR(255),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear la tabla Departamento
CREATE TABLE "Departamento" (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

-- Crear la tabla Ciudad
CREATE TABLE "Ciudad" (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    departamento_id INTEGER NOT NULL,
    FOREIGN KEY (departamento_id) REFERENCES "Departamento" (id) ON DELETE CASCADE
);

-- Tabla Direccion
CREATE TABLE "Direccion" (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES "Cliente"(id) ON DELETE CASCADE,
    tienda_id INTEGER REFERENCES "Tienda"(id) ON DELETE CASCADE,
    direccion TEXT NOT NULL,
    ciudad VARCHAR(100) REFERENCES "Ciudad"(id) ON DELETE CASCADE,
    departamento VARCHAR(100) REFERENCES "Departamento"(id) ON DELETE CASCADE,
    codigo_postal VARCHAR(10),
    principal BOOLEAN DEFAULT FALSE
);

-- Tabla Categoria
CREATE TABLE "Categoria" (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT CHECK (length(descripcion) <= 150)
);

-- Tabla Producto
CREATE TABLE "Producto" (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER REFERENCES "Categoria"(id) ON DELETE CASCADE,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT CHECK (length(descripcion) <= 255),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla Proveedor
CREATE TABLE "Proveedor" (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    razon_social VARCHAR(150) NOT NULL,
    email VARCHAR(100),
    telefono VARCHAR(20),
    direccion TEXT,
    estado VARCHAR(50) CHECK (estado IN ('activo', 'inactivo')) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla ProductosTiendas
CREATE TABLE "ProductosTiendas" (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER REFERENCES "Producto"(id) ON DELETE CASCADE,
    proveedor_id INTEGER REFERENCES "Proveedor"(id) ON DELETE CASCADE,
    tienda_id INTEGER REFERENCES "Tienda"(id) ON DELETE CASCADE,
    precio_unitario DECIMAL(10, 2) DEFAULT 0,
    cantidad INTEGER NOT NULL,
    estado VARCHAR(50) CHECK (estado IN ('activo', 'inactivo')) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    imagen VARCHAR(255)
);

-- Tabla Promocion
CREATE TABLE "Promocion" (
    id SERIAL PRIMARY KEY,
    tienda_id INTEGER REFERENCES "Tienda"(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    descuento DECIMAL(5, 2) NOT NULL,
    tipo_descuento VARCHAR(50),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- Tabla Venta
CREATE TABLE "Venta" (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES "Cliente"(id) ON DELETE CASCADE,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10, 2) NOT NULL
);

-- Tabla DetalleVenta
CREATE TABLE "DetalleVenta" (
    id SERIAL PRIMARY KEY,
    venta_id INTEGER REFERENCES "Venta"(id) ON DELETE CASCADE,
    producto_tienda_id INTEGER REFERENCES "ProductosTiendas"(id) ON DELETE CASCADE,
    cantidad INTEGER NOT NULL,
    precio DECIMAL(10, 2) NOT NULL
);

-- Tabla Inventario
CREATE TABLE "Inventario" (
    id SERIAL PRIMARY KEY,
    producto_tienda_id INTEGER REFERENCES "ProductosTiendas"(id) ON DELETE CASCADE,
    tienda_id INTEGER REFERENCES "Tienda"(id) ON DELETE CASCADE,
    cantidad INTEGER NOT NULL CHECK (cantidad >= 0)
);

-- Tabla MetodoPago
CREATE TABLE "MetodoPago" (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    descripcion TEXT
);

-- Tabla AtencionCliente
CREATE TABLE "AtencionCliente" (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES "Cliente"(id) ON DELETE CASCADE,
    asunto VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    estado VARCHAR(50) CHECK (estado IN ('abierto', 'en progreso', 'cerrado')) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Carrito (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES Cliente(id) ON DELETE CASCADE,
    producto_tienda_id INTEGER REFERENCES ProductosTiendas(id) ON DELETE CASCADE,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ReseñaProducto (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES Cliente(id) ON DELETE CASCADE,
    producto_id INTEGER REFERENCES Producto(id) ON DELETE CASCADE,
    calificacion INTEGER CHECK (calificacion >= 1 AND calificacion <= 5),
    comentario TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE HistorialPrecioProducto (
    id SERIAL PRIMARY KEY,
    producto_tienda_id INTEGER REFERENCES ProductosTiendas(id) ON DELETE CASCADE,
    precio_anterior DECIMAL(10, 2) NOT NULL,
    precio_nuevo DECIMAL(10, 2) NOT NULL CHECK (precio_nuevo >= precio_anterior),
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE EstadoPedido (
    id SERIAL PRIMARY KEY,
    venta_id INTEGER REFERENCES Venta(id) ON DELETE CASCADE,
    estado VARCHAR(50) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comentarios TEXT
);

select * from "Producto"
select * from "Proveedor"
select * from "ProductosTiendas"
select * from "auth_user"
select * from "Cliente"
select * from "Tienda"
select * from "Categoria"
select * from "Direccion"
select * from "Departamento"	
select * from "Ciudad"
select * from "ordenes"

SELECT username, password FROM auth_user WHERE username = 'vamunozf';

-- Insertar datos en Departamento
INSERT INTO "Departamento" (nombre) VALUES
('Antioquia'),
('Atlántico'),
('Bogotá D.C.'),
('Bolívar'),
('Boyacá'),
('Caldas'),
('Caquetá'),
('Casanare'),
('Cauca'),
('Cesar'),
('Chocó'),
('Córdoba'),
('Cundinamarca'),
('Guainía'),
('Guaviare'),
('Guajira'),
('Huila'),
('La Guajira'),
('Magdalena'),
('Meta'),
('Nariño'),
('Norte de Santander'),
('Putumayo'),
('Quindío'),
('Risaralda'),
('San Andrés y Providencia'),
('Santander'),
('Sucre'),
('Tolima'),
('Valle del Cauca'),
('Vaupés'),
('Vichada')
ON CONFLICT (nombre) DO NOTHING;

-- Insertar datos en Ciudad
-- Antioquia
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Medellín', (SELECT id FROM "Departamento" WHERE nombre='Antioquia')),
('Envigado', (SELECT id FROM "Departamento" WHERE nombre='Antioquia')),
('Rionegro', (SELECT id FROM "Departamento" WHERE nombre='Antioquia')),
('Bello', (SELECT id FROM "Departamento" WHERE nombre='Antioquia'))
ON CONFLICT (nombre) DO NOTHING;

-- Atlántico
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Barranquilla', (SELECT id FROM "Departamento" WHERE nombre='Atlántico')),
('Soledad', (SELECT id FROM "Departamento" WHERE nombre='Atlántico')),
('Malambo', (SELECT id FROM "Departamento" WHERE nombre='Atlántico')),
('Sabanalarga', (SELECT id FROM "Departamento" WHERE nombre='Atlántico'))
ON CONFLICT (nombre) DO NOTHING;

-- Bogotá D.C.
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Bogotá', (SELECT id FROM "Departamento" WHERE nombre='Bogotá D.C.'))
ON CONFLICT (nombre) DO NOTHING;

-- Bolívar
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Cartagena', (SELECT id FROM "Departamento" WHERE nombre='Bolívar')),
('Magangué', (SELECT id FROM "Departamento" WHERE nombre='Bolívar')),
('Turbaco', (SELECT id FROM "Departamento" WHERE nombre='Bolívar')),
('Arjona', (SELECT id FROM "Departamento" WHERE nombre='Bolívar'))
ON CONFLICT (nombre) DO NOTHING;

-- Boyacá
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Tunja', (SELECT id FROM "Departamento" WHERE nombre='Boyacá')),
('Duitama', (SELECT id FROM "Departamento" WHERE nombre='Boyacá')),
('Sogamoso', (SELECT id FROM "Departamento" WHERE nombre='Boyacá')),
('Chiquinquirá', (SELECT id FROM "Departamento" WHERE nombre='Boyacá'))
ON CONFLICT (nombre) DO NOTHING;

-- Caldas
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Manizales', (SELECT id FROM "Departamento" WHERE nombre='Caldas')),
('Chinchiná', (SELECT id FROM "Departamento" WHERE nombre='Caldas')),
('Villamaría', (SELECT id FROM "Departamento" WHERE nombre='Caldas')),
('Neira', (SELECT id FROM "Departamento" WHERE nombre='Caldas'))
ON CONFLICT (nombre) DO NOTHING;

-- Caquetá
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Florencia', (SELECT id FROM "Departamento" WHERE nombre='Caquetá')),
('Morelia', (SELECT id FROM "Departamento" WHERE nombre='Caquetá')),
('San Vicente del Caguán', (SELECT id FROM "Departamento" WHERE nombre='Caquetá')),
('El Paujil', (SELECT id FROM "Departamento" WHERE nombre='Caquetá'))
ON CONFLICT (nombre) DO NOTHING;

-- Casanare
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Yopal', (SELECT id FROM "Departamento" WHERE nombre='Casanare')),
('Hato Corozal', (SELECT id FROM "Departamento" WHERE nombre='Casanare')),
('Támara', (SELECT id FROM "Departamento" WHERE nombre='Casanare')),
('Villanueva', (SELECT id FROM "Departamento" WHERE nombre='Casanare'))
ON CONFLICT (nombre) DO NOTHING;

-- Cauca
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Popayán', (SELECT id FROM "Departamento" WHERE nombre='Cauca')),
('Santander de Quilichao', (SELECT id FROM "Departamento" WHERE nombre='Cauca')),
('Piendamó', (SELECT id FROM "Departamento" WHERE nombre='Cauca')),
('Cajibío', (SELECT id FROM "Departamento" WHERE nombre='Cauca'))
ON CONFLICT (nombre) DO NOTHING;

-- Cesar
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Valledupar', (SELECT id FROM "Departamento" WHERE nombre='Cesar')),
('La Paz', (SELECT id FROM "Departamento" WHERE nombre='Cesar')),
('Aguachica', (SELECT id FROM "Departamento" WHERE nombre='Cesar')),
('Bosconia', (SELECT id FROM "Departamento" WHERE nombre='Cesar'))
ON CONFLICT (nombre) DO NOTHING;

-- Chocó
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Quibdó', (SELECT id FROM "Departamento" WHERE nombre='Chocó')),
('Istmina', (SELECT id FROM "Departamento" WHERE nombre='Chocó')),
('Condoto', (SELECT id FROM "Departamento" WHERE nombre='Chocó')),
('Riosucio', (SELECT id FROM "Departamento" WHERE nombre='Chocó'))
ON CONFLICT (nombre) DO NOTHING;

-- Córdoba
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Montería', (SELECT id FROM "Departamento" WHERE nombre='Córdoba')),
('Lorica', (SELECT id FROM "Departamento" WHERE nombre='Córdoba')),
('Cereté', (SELECT id FROM "Departamento" WHERE nombre='Córdoba')),
('Planeta Rica', (SELECT id FROM "Departamento" WHERE nombre='Córdoba'))
ON CONFLICT (nombre) DO NOTHING;

-- Cundinamarca
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Bogotá', (SELECT id FROM "Departamento" WHERE nombre='Cundinamarca')),
('Soacha', (SELECT id FROM "Departamento" WHERE nombre='Cundinamarca')),
('Zipaquirá', (SELECT id FROM "Departamento" WHERE nombre='Cundinamarca')),
('Chía', (SELECT id FROM "Departamento" WHERE nombre='Cundinamarca'))
ON CONFLICT (nombre) DO NOTHING;

-- Guainía
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Inírida', (SELECT id FROM "Departamento" WHERE nombre='Guainía')),
('San Felipe', (SELECT id FROM "Departamento" WHERE nombre='Guainía')),
('La Guadalupe', (SELECT id FROM "Departamento" WHERE nombre='Guainía')),
('Pana Pana', (SELECT id FROM "Departamento" WHERE nombre='Guainía'))
ON CONFLICT (nombre) DO NOTHING;

-- Guaviare
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('San José del Guaviare', (SELECT id FROM "Departamento" WHERE nombre='Guaviare')),
('Calamar', (SELECT id FROM "Departamento" WHERE nombre='Guaviare')),
('El Retorno', (SELECT id FROM "Departamento" WHERE nombre='Guaviare')),
('Miraflores', (SELECT id FROM "Departamento" WHERE nombre='Guaviare'))
ON CONFLICT (nombre) DO NOTHING;

-- La Guajira
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Riohacha', (SELECT id FROM "Departamento" WHERE nombre='La Guajira')),
('Maicao', (SELECT id FROM "Departamento" WHERE nombre='La Guajira')),
('Uribia', (SELECT id FROM "Departamento" WHERE nombre='La Guajira')),
('Fonseca', (SELECT id FROM "Departamento" WHERE nombre='La Guajira'))
ON CONFLICT (nombre) DO NOTHING;

-- Huila
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Neiva', (SELECT id FROM "Departamento" WHERE nombre='Huila')),
('Pitalito', (SELECT id FROM "Departamento" WHERE nombre='Huila')),
('La Plata', (SELECT id FROM "Departamento" WHERE nombre='Huila')),
('Campoalegre', (SELECT id FROM "Departamento" WHERE nombre='Huila'))
ON CONFLICT (nombre) DO NOTHING;

-- Magdalena
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Santa Marta', (SELECT id FROM "Departamento" WHERE nombre='Magdalena')),
('Ciénaga', (SELECT id FROM "Departamento" WHERE nombre='Magdalena')),
('El Rodadero', (SELECT id FROM "Departamento" WHERE nombre='Magdalena')),
('Aracataca', (SELECT id FROM "Departamento" WHERE nombre='Magdalena'))
ON CONFLICT (nombre) DO NOTHING;

-- Meta
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Villavicencio', (SELECT id FROM "Departamento" WHERE nombre='Meta')),
('Acacías', (SELECT id FROM "Departamento" WHERE nombre='Meta')),
('Cumaral', (SELECT id FROM "Departamento" WHERE nombre='Meta')),
('Restrepo', (SELECT id FROM "Departamento" WHERE nombre='Meta'))
ON CONFLICT (nombre) DO NOTHING;

-- Nariño
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Pasto', (SELECT id FROM "Departamento" WHERE nombre='Nariño')),
('Tumaco', (SELECT id FROM "Departamento" WHERE nombre='Nariño')),
('Ipiales', (SELECT id FROM "Departamento" WHERE nombre='Nariño')),
('Sandona', (SELECT id FROM "Departamento" WHERE nombre='Nariño'))
ON CONFLICT (nombre) DO NOTHING;

-- Norte de Santander
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Cúcuta', (SELECT id FROM "Departamento" WHERE nombre='Norte de Santander')),
('Pamplona', (SELECT id FROM "Departamento" WHERE nombre='Norte de Santander')),
('Villa de Rosario', (SELECT id FROM "Departamento" WHERE nombre='Norte de Santander')),
('Ocaña', (SELECT id FROM "Departamento" WHERE nombre='Norte de Santander'))
ON CONFLICT (nombre) DO NOTHING;

-- Putumayo
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Mocoa', (SELECT id FROM "Departamento" WHERE nombre='Putumayo')),
('Villagarzón', (SELECT id FROM "Departamento" WHERE nombre='Putumayo')),
('Leguízamo', (SELECT id FROM "Departamento" WHERE nombre='Putumayo')),
('Puerto Asís', (SELECT id FROM "Departamento" WHERE nombre='Putumayo'))
ON CONFLICT (nombre) DO NOTHING;

-- Quindío
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Armenia', (SELECT id FROM "Departamento" WHERE nombre='Quindío')),
('Calarcá', (SELECT id FROM "Departamento" WHERE nombre='Quindío')),
('Montenegro', (SELECT id FROM "Departamento" WHERE nombre='Quindío')),
('Quimbaya', (SELECT id FROM "Departamento" WHERE nombre='Quindío'))
ON CONFLICT (nombre) DO NOTHING;

-- Risaralda
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Pereira', (SELECT id FROM "Departamento" WHERE nombre='Risaralda')),
('Dosquebradas', (SELECT id FROM "Departamento" WHERE nombre='Risaralda')),
('Santa Rosa de Cabal', (SELECT id FROM "Departamento" WHERE nombre='Risaralda')),
('La Virginia', (SELECT id FROM "Departamento" WHERE nombre='Risaralda'))
ON CONFLICT (nombre) DO NOTHING;

-- San Andrés y Providencia
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('San Andrés', (SELECT id FROM "Departamento" WHERE nombre='San Andrés y Providencia')),
('Providencia', (SELECT id FROM "Departamento" WHERE nombre='San Andrés y Providencia'))
ON CONFLICT (nombre) DO NOTHING;

-- Santander
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Bucaramanga', (SELECT id FROM "Departamento" WHERE nombre='Santander')),
('Floridablanca', (SELECT id FROM "Departamento" WHERE nombre='Santander')),
('Girón', (SELECT id FROM "Departamento" WHERE nombre='Santander')),
('Barrancabermeja', (SELECT id FROM "Departamento" WHERE nombre='Santander'))
ON CONFLICT (nombre) DO NOTHING;

-- Sucre
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Sincelejo', (SELECT id FROM "Departamento" WHERE nombre='Sucre')),
('Corozal', (SELECT id FROM "Departamento" WHERE nombre='Sucre')),
('Sampués', (SELECT id FROM "Departamento" WHERE nombre='Sucre')),
('Morroa', (SELECT id FROM "Departamento" WHERE nombre='Sucre'))
ON CONFLICT (nombre) DO NOTHING;

-- Tolima
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Ibagué', (SELECT id FROM "Departamento" WHERE nombre='Tolima')),
('Lérida', (SELECT id FROM "Departamento" WHERE nombre='Tolima')),
('Espinal', (SELECT id FROM "Departamento" WHERE nombre='Tolima')),
('Honda', (SELECT id FROM "Departamento" WHERE nombre='Tolima'))
ON CONFLICT (nombre) DO NOTHING;

-- Valle del Cauca
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Cali', (SELECT id FROM "Departamento" WHERE nombre='Valle del Cauca')),
('Palmira', (SELECT id FROM "Departamento" WHERE nombre='Valle del Cauca')),
('Buenaventura', (SELECT id FROM "Departamento" WHERE nombre='Valle del Cauca')),
('Tuluá', (SELECT id FROM "Departamento" WHERE nombre='Valle del Cauca'))
ON CONFLICT (nombre) DO NOTHING;

-- Vaupés
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Mitú', (SELECT id FROM "Departamento" WHERE nombre='Vaupés')),
('Pacoa', (SELECT id FROM "Departamento" WHERE nombre='Vaupés')),
('Carurú', (SELECT id FROM "Departamento" WHERE nombre='Vaupés')),
('Cumaribo', (SELECT id FROM "Departamento" WHERE nombre='Vaupés'))
ON CONFLICT (nombre) DO NOTHING;

-- Vichada
INSERT INTO "Ciudad" (nombre, departamento_id) VALUES
('Puerto Carreño', (SELECT id FROM "Departamento" WHERE nombre='Vichada')),
('La Primavera', (SELECT id FROM "Departamento" WHERE nombre='Vichada')),
('Cumaribo', (SELECT id FROM "Departamento" WHERE nombre='Vichada')),
('San José del Guaviare', (SELECT id FROM "Departamento" WHERE nombre='Vichada'))
ON CONFLICT (nombre) DO NOTHING;
