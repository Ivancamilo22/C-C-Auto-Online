-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 20-10-2025 a las 19:29:46
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `concesionario`
--

DELIMITER $$
--
-- Procedimientos
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `insertar_cliente` (IN `p_nombre` VARCHAR(50), IN `p_apellido` VARCHAR(50), IN `p_email` VARCHAR(100), IN `p_telefono` VARCHAR(20), IN `p_direccion` TEXT, IN `p_tipo_documento` VARCHAR(20), IN `p_numero_documento` VARCHAR(20))   BEGIN
    INSERT INTO clientes (nombre, apellido, email, telefono, direccion, tipo_documento, numero_documento)
    VALUES (p_nombre, p_apellido, p_email, p_telefono, p_direccion, p_tipo_documento, p_numero_documento);
    
    SELECT CONCAT('Cliente ', p_nombre, ' ', p_apellido, ' registrado. ID: ', LAST_INSERT_ID()) AS mensaje;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `realizar_venta` (IN `p_cliente_id` INT, IN `p_empleado_id` INT, IN `p_vehiculo_id` INT, IN `p_cantidad` INT, IN `p_metodo_pago` VARCHAR(20))   BEGIN
    DECLARE v_precio DECIMAL(12,2);
    DECLARE v_subtotal DECIMAL(12,2);
    DECLARE v_impuesto DECIMAL(12,2);
    DECLARE v_total DECIMAL(12,2);
    DECLARE v_venta_id INT;
    DECLARE v_stock_actual INT;
    
    -- Verificar stock
    SELECT stock, precio INTO v_stock_actual, v_precio 
    FROM vehiculos 
    WHERE id = p_vehiculo_id;
    
    IF v_stock_actual >= p_cantidad THEN
        -- Calcular montos
        SET v_subtotal = v_precio * p_cantidad;
        SET v_impuesto = v_subtotal * 0.19; -- 19% IVA Colombia
        SET v_total = v_subtotal + v_impuesto;
        
        -- Insertar venta principal
        INSERT INTO ventas (cliente_id, empleado_id, vehiculo_id, subtotal, impuesto, total, metodo_pago)
        VALUES (p_cliente_id, p_empleado_id, p_vehiculo_id, v_subtotal, v_impuesto, v_total, p_metodo_pago);
        
        SET v_venta_id = LAST_INSERT_ID();
        
        -- Insertar detalle de venta
        INSERT INTO detalle_ventas (venta_id, vehiculo_id, cantidad, precio_unitario, subtotal)
        VALUES (v_venta_id, p_vehiculo_id, p_cantidad, v_precio, v_subtotal);
        
        SELECT CONCAT('Venta realizada exitosamente. Nº Venta: ', v_venta_id, ' - Total: $', FORMAT(v_total, 2)) AS mensaje;
    ELSE
        SELECT 'Error: Stock insuficiente' AS mensaje;
    END IF;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `reporte_ventas_mensual` (IN `p_mes` INT, IN `p_año` INT)   BEGIN
    SELECT 
        v.venta_id,
        CONCAT(c.nombre, ' ', c.apellido) AS cliente,
        CONCAT(e.nombre, ' ', e.apellido) AS vendedor,
        vh.nombre AS vehiculo,
        v.total,
        v.fecha_venta,
        v.estado
    FROM ventas v
    JOIN clientes c ON v.cliente_id = c.cliente_id
    JOIN empleados e ON v.empleado_id = e.empleado_id
    LEFT JOIN vehiculos vh ON v.vehiculo_id = vh.id
    WHERE MONTH(v.fecha_venta) = p_mes AND YEAR(v.fecha_venta) = p_año
    ORDER BY v.fecha_venta DESC;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `categoria_id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`categoria_id`, `nombre`, `descripcion`) VALUES
(1, 'Económico', 'Vehículos económicos y eficientes para uso urbano'),
(2, 'Compacto', 'Vehículos compactos versátiles'),
(3, 'Familiar', 'SUVs y vehículos familiares espaciosos'),
(4, 'Premium', 'Vehículos de lujo y alta gama'),
(5, 'Deportivo', 'Vehículos deportivos de alto rendimiento'),
(6, 'XL', 'Vehículos de pasajeros con alta capacidad'),
(7, 'Carga', 'Camiones y vehículos de carga comercial');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `citas_prueba_manejo`
--

CREATE TABLE `citas_prueba_manejo` (
  `cita_id` int(11) NOT NULL,
  `cliente_id` int(11) NOT NULL,
  `vehiculo_id` int(11) NOT NULL,
  `fecha_cita` datetime NOT NULL,
  `empleado_asignado` int(11) DEFAULT NULL,
  `estado` enum('Programada','Completada','Cancelada') DEFAULT 'Programada',
  `notas` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `cliente_id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` text DEFAULT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  `tipo_documento` enum('DNI','Cedula','Pasaporte') DEFAULT 'Cedula',
  `numero_documento` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_ventas`
--

CREATE TABLE `detalle_ventas` (
  `detalle_id` int(11) NOT NULL,
  `venta_id` int(11) NOT NULL,
  `vehiculo_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL DEFAULT 1,
  `precio_unitario` decimal(12,2) NOT NULL,
  `descuento` decimal(10,2) DEFAULT 0.00,
  `subtotal` decimal(12,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Disparadores `detalle_ventas`
--
DELIMITER $$
CREATE TRIGGER `after_venta_insert` AFTER INSERT ON `detalle_ventas` FOR EACH ROW BEGIN
    UPDATE vehiculos 
    SET stock = stock - NEW.cantidad 
    WHERE id = NEW.vehiculo_id;
    
    INSERT INTO inventario_movimientos (vehiculo_id, tipo, cantidad, motivo)
    VALUES (NEW.vehiculo_id, 'Salida', NEW.cantidad, 'Venta realizada');
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `before_venta_insert` BEFORE INSERT ON `detalle_ventas` FOR EACH ROW BEGIN
    SET NEW.subtotal = (NEW.precio_unitario * NEW.cantidad) - NEW.descuento;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empleados`
--

CREATE TABLE `empleados` (
  `empleado_id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `apellido` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `puesto` enum('Vendedor','Gerente','Administrativo','Mecánico') NOT NULL,
  `fecha_contratacion` date NOT NULL,
  `salario` decimal(10,2) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empleados`
--

INSERT INTO `empleados` (`empleado_id`, `nombre`, `apellido`, `email`, `telefono`, `puesto`, `fecha_contratacion`, `salario`, `activo`) VALUES
(1, 'Juan', 'Pérez', 'juan.perez@concesionario.com', '3001234567', 'Vendedor', '2024-01-15', 2500000.00, 1),
(2, 'María', 'González', 'maria.gonzalez@concesionario.com', '3009876543', 'Gerente', '2023-06-01', 4500000.00, 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `inventario_movimientos`
--

CREATE TABLE `inventario_movimientos` (
  `movimiento_id` int(11) NOT NULL,
  `vehiculo_id` int(11) NOT NULL,
  `tipo` enum('Entrada','Salida','Ajuste') NOT NULL,
  `cantidad` int(11) NOT NULL,
  `fecha_movimiento` datetime DEFAULT current_timestamp(),
  `motivo` varchar(200) DEFAULT NULL,
  `referencia` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `user_type` varchar(20) NOT NULL DEFAULT 'client',
  `profile_image` varchar(255) DEFAULT 'uploads/default_avatar.png',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `phone`, `password`, `user_type`, `profile_image`, `created_at`) VALUES
(1, 'admin', 'admin@concesionario.com', '3001234567', '$2b$12$5o5vwFa3ALTdOaLhYaJiTO5rt.bAeSyIfgWhtPX/7KywiyM8ce5Ve', 'admin', 'uploads/default_avatar.png', '2025-10-20 16:30:38'),
(2, 'IvanCamilo22', 'ivancarrascocano@gmail.com', '3024649720', '$2b$12$MECJYMpy1m6gZwrsabIVIuLSNMsvAj0Kn/lPDNcq0jKdkQBw9lNh.', 'admin', 'uploads/IvanCamilo22_IvanCamilo22_8YfAkqH3p_Y.jpeg', '2025-10-20 17:03:02');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `vehiculos`
--

CREATE TABLE `vehiculos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `categoria` varchar(50) NOT NULL,
  `capacidad_personas` int(11) NOT NULL,
  `capacidad_maletas` int(11) NOT NULL,
  `transmision` varchar(20) NOT NULL,
  `aire_acondicionado` tinyint(1) NOT NULL DEFAULT 1,
  `precio` decimal(15,2) NOT NULL,
  `descuento_soat` varchar(20) DEFAULT NULL,
  `descripcion` text NOT NULL,
  `imagen` varchar(255) NOT NULL,
  `destacado` tinyint(1) NOT NULL DEFAULT 0,
  `stock` int(11) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `vehiculos`
--

INSERT INTO `vehiculos` (`id`, `nombre`, `categoria`, `capacidad_personas`, `capacidad_maletas`, `transmision`, `aire_acondicionado`, `precio`, `descuento_soat`, `descripcion`, `imagen`, `destacado`, `stock`, `created_at`) VALUES
(1, 'Chevrolet Spark-GT', 'economico', 4, 2, 'Manual', 1, 24000000.00, '-15% SOAT', 'Perfecto para la ciudad y viajes cortos. Bajo consumo de combustible.', 'Media/Spark-GT.png', 0, 5, '2025-10-20 16:30:38'),
(2, 'Kia Picanto', 'economico', 4, 2, 'Manual', 1, 53990000.00, '-15% SOAT', 'Compacto, eficiente y fácil de maniobrar en entornos urbanos.', 'Media/Picanto.png', 0, 3, '2025-10-20 16:30:38'),
(3, 'Renault Kwid', 'economico', 4, 2, 'Manual', 1, 54190000.00, '-15% SOAT', 'Diseñado para la ciudad, con un precio competitivo y buen rendimiento.', 'Media/Kwid.png', 0, 4, '2025-10-20 16:30:38'),
(4, 'Mazda 2', 'compacto', 5, 3, 'Manual', 1, 79050000.00, '-15% SOAT', 'Diseño elegante, manejo suave y eficiente en consumo.', 'Media/2.png', 0, 6, '2025-10-20 16:30:38'),
(5, 'Suzuki Swift', 'compacto', 5, 3, 'Automático', 1, 65000000.00, '-15% SOAT', 'Atractivo, ágil y con buena relación costo-beneficio.', 'Media/Swift.jpg', 0, 4, '2025-10-20 16:30:38'),
(6, 'Chevrolet Onix', 'compacto', 5, 3, 'Automático', 1, 77450000.00, '-15% SOAT', 'Tecnología funcional y confort a un precio accesible.', 'Media/Onix.png', 0, 5, '2025-10-20 16:30:38'),
(7, 'Renault Duster', 'familiar', 5, 5, 'Automático', 1, 88400000.00, '-20% SOAT', 'SUV robusto y versátil, con amplio espacio interior.', 'Media/Duster.png', 0, 3, '2025-10-20 16:30:38'),
(8, 'Chevrolet Tracker', 'familiar', 7, 4, 'Manual', 1, 104990000.00, '-20% SOAT', 'SUV compacto, confortable y sólido para uso familiar.', 'Media/Tracker.webp', 0, 2, '2025-10-20 16:30:38'),
(9, 'Toyota Hilux', 'familiar', 5, 5, 'Automático', 1, 110000000.00, '-20% SOAT', 'Pick-up resistente y potente, con gran capacidad de carga.', 'Media/Hilux.png', 1, 4, '2025-10-20 16:30:38'),
(10, 'Toyota Corolla Cross', 'premium', 5, 3, 'Automático', 1, 115000000.00, '-10% SOAT', 'SUV híbrido que destaca por su eficiencia y confort.', 'Media/Corolla.png', 0, 2, '2025-10-20 16:30:38'),
(11, 'Mazda CX-5', 'premium', 5, 3, 'Automático', 1, 149750000.00, '-10% SOAT', 'SUV sofisticado con excelente calidad de construcción.', 'Media/CX-5.jpg', 0, 2, '2025-10-20 16:30:38'),
(12, 'Toyota Prado', 'premium', 5, 3, 'Automático', 1, 299000000.00, '-10% SOAT', 'SUV de lujo, reconocido por su durabilidad y capacidad todoterreno.', 'Media/Prado.jpg', 1, 1, '2025-10-20 16:30:38'),
(13, 'Chevrolet Camaro ZL1', 'Deportivo', 5, 3, 'Automático', 1, 350000000.00, '-10% SOAT', 'Potente motor V8 de 6.2 litros con 650 caballos de fuerza, alcanzando 100 km/h en 3.6 segundos.', 'Media/Camaro.jpg', 1, 1, '2025-10-20 16:30:38'),
(14, 'Ford Mustang GT', 'Deportivo', 5, 3, 'Automático', 1, 250000000.00, '-20% SOAT', 'Clásico muscle car estadounidense con potente motor V8 y diseño icónico.', 'Media/Mustang.jpg', 0, 2, '2025-10-20 16:30:38'),
(15, 'Chevrolet N400', 'XL', 7, 3, 'Automático', 1, 85000000.00, '-20% SOAT', 'Se destaca por su maniobrabilidad, eficiencia de combustible y diseño práctico con múltiples accesos.', 'Media/N400.png', 1, 3, '2025-10-20 16:30:38'),
(16, 'Mercedes-Benz Sprinter', 'XL', 15, 3, 'Automático', 1, 150000000.00, '-20% SOAT', 'Ofrece una conducción confortable y está equipada con tecnología moderna para seguridad y eficiencia.', 'Media/Sprinter.png', 0, 2, '2025-10-20 16:30:38'),
(17, 'Chevrolet NHR Reward', 'XL', 3, 0, 'Manual', 1, 95000000.00, '-25% SOAT', 'Camión ligero ideal para distribución urbana. Capacidad de carga de 3.5 toneladas, motor diésel eficiente.', 'Media/nhr-seca.jpg', 0, 4, '2025-10-20 16:30:38'),
(18, 'Isuzu NQR', 'XL', 3, 0, 'Manual', 1, 125000000.00, '-25% SOAT', 'Camión mediano robusto con capacidad de 5 toneladas. Perfecto para transporte intermunicipales.', 'Media/npr-xd_diesel.webp', 1, 3, '2025-10-20 16:30:38'),
(19, 'Ford Cargo 1723', 'XL', 3, 0, 'Manual', 1, 180000000.00, '-25% SOAT', 'Camión pesado para transporte de gran volumen. Motor potente turbo diésel con capacidad de 8 toneladas.', 'Media/3.jpg', 0, 2, '2025-10-20 16:30:38');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

CREATE TABLE `ventas` (
  `venta_id` int(11) NOT NULL,
  `cliente_id` int(11) NOT NULL,
  `empleado_id` int(11) NOT NULL,
  `vehiculo_id` int(11) DEFAULT NULL,
  `fecha_venta` datetime DEFAULT current_timestamp(),
  `subtotal` decimal(12,2) NOT NULL,
  `impuesto` decimal(12,2) NOT NULL,
  `total` decimal(12,2) NOT NULL,
  `estado` enum('Pendiente','Pagada','Entregada','Cancelada') DEFAULT 'Pendiente',
  `metodo_pago` enum('Efectivo','Tarjeta','Transferencia','Financiamiento') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_inventario`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vista_inventario` (
`id` int(11)
,`nombre` varchar(100)
,`categoria` varchar(50)
,`precio` decimal(15,2)
,`stock` int(11)
,`destacado` tinyint(1)
,`estado_stock` varchar(10)
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_ventas_recientes`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `vista_ventas_recientes` (
`venta_id` int(11)
,`fecha_venta` datetime
,`cliente` varchar(101)
,`vendedor` varchar(101)
,`vehiculo` varchar(100)
,`total` decimal(12,2)
,`estado` enum('Pendiente','Pagada','Entregada','Cancelada')
,`metodo_pago` enum('Efectivo','Tarjeta','Transferencia','Financiamiento')
);

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_inventario`
--
DROP TABLE IF EXISTS `vista_inventario`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_inventario`  AS SELECT `v`.`id` AS `id`, `v`.`nombre` AS `nombre`, `v`.`categoria` AS `categoria`, `v`.`precio` AS `precio`, `v`.`stock` AS `stock`, `v`.`destacado` AS `destacado`, CASE WHEN `v`.`stock` = 0 THEN 'Agotado' WHEN `v`.`stock` <= 2 THEN 'Stock Bajo' ELSE 'Disponible' END AS `estado_stock` FROM `vehiculos` AS `v` ORDER BY `v`.`categoria` ASC, `v`.`nombre` ASC ;

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_ventas_recientes`
--
DROP TABLE IF EXISTS `vista_ventas_recientes`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_ventas_recientes`  AS SELECT `v`.`venta_id` AS `venta_id`, `v`.`fecha_venta` AS `fecha_venta`, concat(`c`.`nombre`,' ',`c`.`apellido`) AS `cliente`, concat(`e`.`nombre`,' ',`e`.`apellido`) AS `vendedor`, `vh`.`nombre` AS `vehiculo`, `v`.`total` AS `total`, `v`.`estado` AS `estado`, `v`.`metodo_pago` AS `metodo_pago` FROM (((`ventas` `v` join `clientes` `c` on(`v`.`cliente_id` = `c`.`cliente_id`)) join `empleados` `e` on(`v`.`empleado_id` = `e`.`empleado_id`)) left join `vehiculos` `vh` on(`v`.`vehiculo_id` = `vh`.`id`)) ORDER BY `v`.`fecha_venta` DESC LIMIT 0, 50 ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`categoria_id`);

--
-- Indices de la tabla `citas_prueba_manejo`
--
ALTER TABLE `citas_prueba_manejo`
  ADD PRIMARY KEY (`cita_id`),
  ADD KEY `cliente_id` (`cliente_id`),
  ADD KEY `vehiculo_id` (`vehiculo_id`),
  ADD KEY `empleado_asignado` (`empleado_asignado`);

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`cliente_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `numero_documento` (`numero_documento`),
  ADD KEY `idx_clientes_email` (`email`);

--
-- Indices de la tabla `detalle_ventas`
--
ALTER TABLE `detalle_ventas`
  ADD PRIMARY KEY (`detalle_id`),
  ADD KEY `venta_id` (`venta_id`),
  ADD KEY `vehiculo_id` (`vehiculo_id`);

--
-- Indices de la tabla `empleados`
--
ALTER TABLE `empleados`
  ADD PRIMARY KEY (`empleado_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_empleados_puesto` (`puesto`,`activo`);

--
-- Indices de la tabla `inventario_movimientos`
--
ALTER TABLE `inventario_movimientos`
  ADD PRIMARY KEY (`movimiento_id`),
  ADD KEY `vehiculo_id` (`vehiculo_id`);

--
-- Indices de la tabla `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indices de la tabla `vehiculos`
--
ALTER TABLE `vehiculos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_categoria` (`categoria`),
  ADD KEY `idx_precio` (`precio`);

--
-- Indices de la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD PRIMARY KEY (`venta_id`),
  ADD KEY `cliente_id` (`cliente_id`),
  ADD KEY `empleado_id` (`empleado_id`),
  ADD KEY `vehiculo_id` (`vehiculo_id`),
  ADD KEY `idx_ventas_fecha` (`fecha_venta`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `categoria_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `citas_prueba_manejo`
--
ALTER TABLE `citas_prueba_manejo`
  MODIFY `cita_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `cliente_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `detalle_ventas`
--
ALTER TABLE `detalle_ventas`
  MODIFY `detalle_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `empleados`
--
ALTER TABLE `empleados`
  MODIFY `empleado_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `inventario_movimientos`
--
ALTER TABLE `inventario_movimientos`
  MODIFY `movimiento_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `vehiculos`
--
ALTER TABLE `vehiculos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT de la tabla `ventas`
--
ALTER TABLE `ventas`
  MODIFY `venta_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `citas_prueba_manejo`
--
ALTER TABLE `citas_prueba_manejo`
  ADD CONSTRAINT `citas_prueba_manejo_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`cliente_id`),
  ADD CONSTRAINT `citas_prueba_manejo_ibfk_2` FOREIGN KEY (`vehiculo_id`) REFERENCES `vehiculos` (`id`),
  ADD CONSTRAINT `citas_prueba_manejo_ibfk_3` FOREIGN KEY (`empleado_asignado`) REFERENCES `empleados` (`empleado_id`);

--
-- Filtros para la tabla `detalle_ventas`
--
ALTER TABLE `detalle_ventas`
  ADD CONSTRAINT `detalle_ventas_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`venta_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `detalle_ventas_ibfk_2` FOREIGN KEY (`vehiculo_id`) REFERENCES `vehiculos` (`id`);

--
-- Filtros para la tabla `inventario_movimientos`
--
ALTER TABLE `inventario_movimientos`
  ADD CONSTRAINT `inventario_movimientos_ibfk_1` FOREIGN KEY (`vehiculo_id`) REFERENCES `vehiculos` (`id`);

--
-- Filtros para la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`cliente_id`),
  ADD CONSTRAINT `ventas_ibfk_2` FOREIGN KEY (`empleado_id`) REFERENCES `empleados` (`empleado_id`),
  ADD CONSTRAINT `ventas_ibfk_3` FOREIGN KEY (`vehiculo_id`) REFERENCES `vehiculos` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
