-- SCRIPT CORREGIDO: SISTEMA DE ASIGNACION DE HORARIOS DE PROFESORES
-- Crea DB y configura charset
-- DROP DATABASE IF EXISTS sisasigprof;
CREATE DATABASE sisasigprof CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
USE sisasigprof;

-- ===================================================================
-- Tablas maestras / catálogos
-- ===================================================================

CREATE TABLE EstadoUsuario (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    EstadoUs VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE RolesPermisos (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Estados (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Estado VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Aulas (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    NombreAula VARCHAR(50),
    Edificio VARCHAR(50),
    Piso VARCHAR(15),
    Capacidad INT,
    Tipo VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE DiasLab (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    DiaL VARCHAR(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Horas(
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Hora TIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===================================================================
-- Tabla Usuario (credenciales + perfil mínimo)
-- - Username único
-- - Password preparado para hash (VARCHAR(255)), SIN UNIQUE
-- ===================================================================
CREATE TABLE Usuario (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    FechaAlta DATE NOT NULL,
    Username VARCHAR(100) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL UNIQUE,                -- almacenar hash (bcrypt/argon2) en app
    RolId INT DEFAULT 3,
    EstadoUsId INT DEFAULT 1,
    CONSTRAINT fk_usuario_estado FOREIGN KEY (EstadoUsId) REFERENCES EstadoUsuario(Id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_usuario_rol FOREIGN KEY (RolId) REFERENCES RolesPermisos(Id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
select *from Usuario;
-- ===================================================================
-- Tabla Profesor
-- ===================================================================
CREATE TABLE Profesor (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(100),
    ApPat VARCHAR(100),
    ApMat VARCHAR(100),
    NumEmpleado VARCHAR(100) UNIQUE, 
    Direccion VARCHAR(250),
    Email VARCHAR(100) UNIQUE,
    Telefono VARCHAR(30) NULL,
    FechaIngreso DATE,
    EstadoId INT DEFAULT 1,
    Especialidad VARCHAR(100),
    UsuarioId INT NULL,
    AulaId INT NULL,
    CONSTRAINT fk_profesor_usuario FOREIGN KEY (UsuarioId) REFERENCES Usuario(Id) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_profesor_aula FOREIGN KEY (AulaId) REFERENCES Aulas(Id) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_profesor_estado FOREIGN KEY (EstadoId) REFERENCES Estados(Id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
select *from Profesor;
-- ===================================================================
-- Materia y relaciones
-- ===================================================================
CREATE TABLE Materia (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(100) NOT NULL,
    Codigo VARCHAR(20),
    DuracionMinutos INT DEFAULT 60,
    ProfesorId INT NULL,
    CONSTRAINT fk_materia_profesor FOREIGN KEY (ProfesorId) REFERENCES Profesor(Id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Horario (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    DiaId INT NOT NULL, 
    HorarioInicioId INT NOT NULL,
    HoraFinId INT NOT NULL,
    CONSTRAINT fk_horario_dia FOREIGN KEY (DiaId) REFERENCES DiasLab(Id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_horario_inicio FOREIGN KEY (HorarioInicioId) REFERENCES Horas(Id) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_horario_fin FOREIGN KEY (HoraFinId) REFERENCES Horas(Id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE AulaHorario (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    NumAula INT,
    AulaId INT NOT NULL,
    HorarioId INT NOT NULL,
    CONSTRAINT fk_aulahorario_aula FOREIGN KEY (AulaId) REFERENCES Aulas(Id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_aulahorario_horario FOREIGN KEY (HorarioId) REFERENCES Horario(Id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE MateriaHorario (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    MateriaId INT NOT NULL,
    HorarioId INT NOT NULL,
    AulaId INT NULL,
    CONSTRAINT fk_mh_materia FOREIGN KEY (MateriaId) REFERENCES Materia(Id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_mh_horario FOREIGN KEY (HorarioId) REFERENCES Horario(Id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_mh_aula FOREIGN KEY (AulaId) REFERENCES Aulas(Id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===================================================================
-- Servicios y reportes
-- ===================================================================
CREATE TABLE EmailServicios (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Destino VARCHAR(100),
    Mensaje TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE PushServicios (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    UsuarioId INT,
    Mensaje TEXT,
    CONSTRAINT fk_push_usuario FOREIGN KEY (UsuarioId) REFERENCES Usuario(Id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE GeneradorReportes (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Contenido TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE RegistroEventos (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Descripcion TEXT,
    Fecha DATE,
    GeneradorReporteId INT,
    UsuarioId INT NULL,
    TipoEvento VARCHAR(50) NULL,
    CONSTRAINT fk_evento_usuario FOREIGN KEY (UsuarioId) REFERENCES Usuario(Id) ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_evento_generador FOREIGN KEY (GeneradorReporteId) REFERENCES GeneradorReportes(Id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE RegistroVisitas (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Usuario VARCHAR(100),
    FechaEntrada DATETIME,
    FechaSalida DATETIME,
    GeneradorReporteId INT,
    CONSTRAINT fk_visitas_generador FOREIGN KEY (GeneradorReporteId) REFERENCES GeneradorReportes(Id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===================================================================
-- Administrador (perfil extendido) -> referenciar Usuario; SIN password redundante
-- ===================================================================
CREATE TABLE Administrador (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    UsuarioId INT UNIQUE,
    -- Eliminamos contraseña duplicada: las credenciales están en Usuario.Password
    CONSTRAINT fk_administrador_usuario FOREIGN KEY (UsuarioId) REFERENCES Usuario(Id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===================================================================
-- Grupos y relaciones
-- ===================================================================
CREATE TABLE Grupo (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(100),
    Cupo INT DEFAULT 30,
    ProfesorId INT,
    CONSTRAINT fk_grupo_profesor FOREIGN KEY (ProfesorId) REFERENCES Profesor(Id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE PreferenciaMateria (
  Id INT PRIMARY KEY AUTO_INCREMENT,
  MateriaId INT NOT NULL,
  ProfesorId INT NOT NULL,
  Ranks INT NOT NULL,
  CONSTRAINT fk_prefMat_materia FOREIGN KEY (MateriaId) REFERENCES Materia(Id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_prefMat_profesor FOREIGN KEY (ProfesorId) REFERENCES Profesor(Id) ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE (MateriaId, ProfesorId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE MateriaGrupo (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    MateriaId INT,
    GrupoId INT,
    CONSTRAINT fk_mg_materia FOREIGN KEY (MateriaId) REFERENCES Materia(Id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_mg_grupo FOREIGN KEY (GrupoId) REFERENCES Grupo(Id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===================================================================
-- Disponibilidad, Preferencias, Capacidad, Asignacion
-- ===================================================================
CREATE TABLE DisponibilidadProfesor (
  Id INT PRIMARY KEY AUTO_INCREMENT,
  ProfesorId INT NOT NULL,
  DiaId INT NOT NULL,
  HorarioInicioId INT NOT NULL,
  HoraFinId INT NOT NULL,
  CONSTRAINT fk_disp_prof FOREIGN KEY (ProfesorId) REFERENCES Profesor(Id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_disp_dia FOREIGN KEY (DiaId) REFERENCES DiasLab(Id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_disp_inicio FOREIGN KEY (HorarioInicioId) REFERENCES Horas(Id) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_disp_fin FOREIGN KEY (HoraFinId) REFERENCES Horas(Id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE PreferenciaProfesor (
  Id INT PRIMARY KEY AUTO_INCREMENT,
  ProfesorId INT NOT NULL,
  MateriaId INT NOT NULL,
  Ranks INT NOT NULL,
  CONSTRAINT fk_prefprof_prof FOREIGN KEY (ProfesorId) REFERENCES Profesor(Id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_prefprof_mat FOREIGN KEY (MateriaId) REFERENCES Materia(Id) ON DELETE CASCADE ON UPDATE CASCADE,
  UNIQUE (ProfesorId, MateriaId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE MateriaCapacidad (
  Id INT PRIMARY KEY AUTO_INCREMENT,
  MateriaId INT NOT NULL,
  Cupo INT NOT NULL DEFAULT 1,
  CONSTRAINT fk_matcap_materia FOREIGN KEY (MateriaId) REFERENCES Materia(Id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE Asignacion (
  Id INT PRIMARY KEY AUTO_INCREMENT,
  ProfesorId INT NOT NULL,
  MateriaId INT NOT NULL,
  HorarioId INT NULL,
  AulaId INT NULL,
  GrupoId INT NULL,
  FechaAsignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  Estado VARCHAR(20) DEFAULT 'activa',
  CONSTRAINT fk_asig_prof FOREIGN KEY (ProfesorId) REFERENCES Profesor(Id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_asig_mat FOREIGN KEY (MateriaId) REFERENCES Materia(Id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_asig_hor FOREIGN KEY (HorarioId) REFERENCES Horario(Id) ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fk_asig_aula FOREIGN KEY (AulaId) REFERENCES Aulas(Id) ON UPDATE CASCADE ON DELETE SET NULL,
  CONSTRAINT fk_asig_grupo FOREIGN KEY (GrupoId) REFERENCES Grupo(Id) ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===================================================================
-- Tablas de pruebas / servicios menores
-- ===================================================================
CREATE TABLE EmailServicios2 (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Destino VARCHAR(100),
    Mensaje TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===================================================================
-- Datos iniciales (ejemplos)
-- ===================================================================
INSERT INTO RolesPermisos (Nombre) VALUES
('Administrador'), ('Administrador del sistema'),
('Profesor'), ('Profesor académico');

INSERT INTO EstadoUsuario (EstadoUs) VALUES
('Activo'), ('Inactivo'), ('Bloqueado');

INSERT INTO Estados (Estado) VALUES
('Activo'), ('Inactivo'), ('Vacaciones'), ('Licencia_Medica'), ('Jubilado');

-- Usuarios: recordar que Password debe guardarse como HASH en aplicación
INSERT INTO Usuario (FechaAlta, Username, Password, RolId, EstadoUsId) VALUES
('2020-01-10', 'cmendoza', 'admin123', 1, 1),
('2020-02-15', 'ltorres', 'admin456', 1, 1),
('2021-03-20', 'arios', 'prof123', 4, 1),
('2021-04-25', 'msanchez', 'prof456', 3, 1),
('2021-05-30', 'sgomez', 'prof789', 3, 1),
('2021-06-10', 'jperez', 'prof321', 3, 1),
('2021-07-15', 'ldiaz', 'prof654', 3, 1),
('2021-08-20', 'mortega', 'prof987', 3, 1),
('2021-09-25', 'evargas', 'prof159', 3, 1);

-- SET FOREIGN_KEY_CHECKS = 0;
-- DELETE FROM Aulas;
INSERT INTO Aulas (Id, NombreAula, Edificio, Piso, Capacidad, Tipo) VALUES
(1, 'Taller de Electrónica', 'Edificio Central', 'Planta Baja', 20, 'Taller'),
(2, 'Taller de Costura', 'Edificio Central', 'Planta Baja', 20, 'Taller'),
(3, 'Taller de Cocina', 'Edificio Central', 'Planta Baja', 20, 'Taller'),
(4, 'Taller de Dibujo Técnico', 'Edificio Central', 'Planta Baja', 20, 'Taller'),
(5, 'Laboratorio de Física y Química', 'Edificio Central', 'Planta Baja', 20, 'Laboratorio'),
(6, 'Aula A', 'Edificio Central', 'Primer Piso', 30, 'Clase'),
(7, 'Aula B', 'Edificio Central', 'Primer Piso', 30, 'Clase'),
(8, 'Aula C', 'Edificio Central', 'Primer Piso', 30, 'Clase'),
(9, 'Aula D', 'Edificio Central', 'Primer Piso', 30, 'Clase'),
(10, 'Aula E', 'Edificio Central', 'Primer Piso', 30, 'Clase'),
(11, 'Aula F', 'Edificio Central', 'Primer Piso', 30, 'Clase'),
(12, 'Aula G', 'Edificio Central', 'Primer Piso', 30, 'Clase'),
(13, 'Aula H', 'Edificio Central', 'Primer Piso', 30, 'Clase'),
(14, 'Aula A', 'Edificio Central', 'Segundo Piso', 30, 'Clase'),
(15, 'Aula B', 'Edificio Central', 'Segundo Piso', 30, 'Clase'),
(16, 'Aula C', 'Edificio Central', 'Segundo Piso', 30, 'Clase'),
(17, 'Aula D', 'Edificio Central', 'Tercer Piso', 30, 'Clase'),
(18, 'Aula E', 'Edificio Central', 'Tercer Piso', 30, 'Clase'),
(19, 'Aula F', 'Edificio Central', 'Tercer Piso', 30, 'Clase'),
(20, 'Taller de MECANICA', 'Edificio Central', 'Planta Baja', 20, 'Taller'),
(21, 'Taller de COMPUTACION', 'Edificio Central', 'Planta Baja', 20, 'Taller');
-- SET FOREIGN_KEY_CHECKS = 1;

-- Horas y dias
INSERT INTO Horas (Hora) VALUES
('07:00:00'), ('07:30:00'), ('08:00:00'), ('08:30:00'), ('09:00:00'),
('09:30:00'), ('10:00:00'), ('10:30:00'), ('11:00:00'), ('11:30:00'),
('12:00:00'), ('12:30:00'), ('13:00:00'), ('13:30:00'), ('14:00:00'),
('14:30:00'), ('15:00:00'), ('15:30:00'), ('16:00:00'), ('16:30:00'),
('17:00:00'), ('17:30:00'), ('18:00:00'), ('18:30:00'), ('19:00:00'),
('19:30:00'), ('20:00:00'), ('20:30:00'), ('21:00:00'), ('21:30:00'),
('22:00:00');

INSERT INTO DiasLab (DiaL) VALUES
('Lunes'),('Martes'),('Miercoles'),('Jueves'),('Viernes');

-- Profesor (UsuarioId debe existir en Usuario)
INSERT INTO Profesor (
  Nombre, ApPat, ApMat, NumEmpleado, Direccion, Email, Telefono, FechaIngreso, EstadoId, Especialidad, UsuarioId, AulaId) VALUES
('Ana', 'Ríos', 'Castillo', 'EMP001', 'Calle Luna 123', 'ana.rios@example.com', '555-1111', '2020-08-15', 1, 'Matemáticas', 3, 1),
('Mario', 'Sánchez', 'Luna', 'EMP002', 'Av. Sol 456', 'mario.sanchez@example.com', '555-2222', '2019-03-10', 1, 'Física', 4, 2),
('Sandra', 'Gómez', 'Fernández', 'EMP003', 'Calle Estrella 789', 'sandra.gomez@example.com', '555-3333', '2021-01-20', 3, 'Biología', 5, 3),
('José', 'Pérez', 'Ramírez', 'EMP004', 'Av. Río 321', 'jose.perez@example.com', '555-4444', '2018-06-05', 4, 'Historia', 6, 4),
('Laura', 'Díaz', 'Morales', 'EMP005', 'Calle Mar 654', 'laura.diaz@example.com', '555-5555', '2022-09-12', 1, 'Lengua y Literatura', 7, 5),
('Miguel', 'Ortega', 'Salinas', 'EMP006', 'Av. Tierra 987', 'miguel.ortega@example.com', '555-6666', '2017-11-30', 5, 'Informática', 8, 6),
('Elena', 'Vargas', 'Torres', 'EMP007', 'Calle Aire 159', 'elena.vargas@example.com', '555-7777', '2023-02-01', 2, 'Química', 9, 7);

-- Materias ejemplo
INSERT INTO Materia (Nombre, Codigo, DuracionMinutos, ProfesorId) VALUES
('Álgebra Lineal', 'MAT101', 90, 1),
('Cálculo Diferencial', 'MAT102', 90, 1),
('Estadística', 'MAT103', 75, 1),
('Física I', 'FIS101', 90, 2),
('Electromagnetismo', 'FIS102', 90, 2),
('Física Moderna', 'FIS103', 75, 2),
('Biología General', 'BIO101', 75, 3),
('Anatomía Humana', 'BIO102', 90, 3),
('Ecología', 'BIO103', 60, 3),
('Historia Universal', 'HIS101', 60, 4),
('Historia de México', 'HIS102', 60, 4),
('Ciencias Sociales', 'HIS103', 60, 4),
('Literatura Clásica', 'LEN101', 60, 5),
('Redacción y Estilo', 'LEN102', 60, 5),
('Análisis Literario', 'LEN103', 75, 5),
('Programación I', 'INF101', 90, 6),
('Bases de Datos', 'INF102', 90, 6),
('Redes de Computadoras', 'INF103', 75, 6),
('Química General', 'QUI101', 75, 7),
('Química Orgánica', 'QUI102', 90, 7),
('Laboratorio de Química', 'QUI103', 120, 7);

-- Horario (ejemplo)
-- DELETE FROM Horario;
INSERT INTO Horario (Id, DiaId, HorarioInicioId, HoraFinId) VALUES
(1, 1, 1, 3), (2, 1, 3, 5), (3, 1, 5, 7), (4, 1, 7, 9), (5, 1, 9, 11),
(6, 2, 1, 3), (7, 2, 3, 5), (8, 2, 5, 7), (9, 2, 7, 9), (10, 2, 9, 11),
(11, 3, 1, 3), (12, 3, 3, 5), (13, 3, 5, 7), (14, 3, 7, 9), (15, 3, 9, 11),
(16, 4, 1, 3), (17, 4, 3, 5), (18, 4, 5, 7), (19, 4, 7, 9),
(20, 5, 1, 3), (21, 5, 3, 5);
-- DELETE FROM MateriaHorario;
-- AulaHorario y MateriaHorario ejemplos (asegúrate de contar con IDs correspondientes)
-- DELETE FROM MateriaHorario;
INSERT INTO MateriaHorario (MateriaId, HorarioId, AulaId) VALUES
(1, 1, 1), (2, 2, 2), (3, 3, 3), (4, 4, 4), (5, 5, 5),
(6, 6, 6), (7, 7, 7), (8, 8, 8), (9, 9, 9), (10, 10, 10),
(11, 11, 11), (12, 12, 12), (13, 13, 13), (14, 14, 14),
(15, 15, 15), (16, 16, 16), (17, 17, 17), (18, 18, 18),
(19, 19, 19), (20, 20, 20), (21, 21, 21) ;
-- omitir (20,20,20) y (21,21,21) hasta que existan esas aulas


-- DELETE FROM AulaHorario;
INSERT INTO AulaHorario (NumAula, AulaId, HorarioId) VALUES
(101, 1, 1), (102, 2, 2), (103, 3, 3), (104, 4, 4),
(105, 5, 5), (106, 6, 6), (107, 7, 7), (108, 8, 8),
(109, 9, 9), (110, 10, 10), (111, 11, 11), (112, 12, 12),
(113, 13, 13), (114, 14, 14), (115, 15, 15), (116, 16, 16),
(117, 17, 17), (118, 18, 18), (119, 19, 19), (120, 20, 20),
(121, 21, 21);

-- Grupos
INSERT INTO Grupo (Nombre, Cupo, ProfesorId) VALUES
('Grupo A1', 30, 1), ('Grupo A2', 28, 1), ('Grupo A3', 32, 1),
('Grupo B1', 30, 2), ('Grupo B2', 30, 2), ('Grupo B3', 29, 2),
('Grupo C1', 25, 3), ('Grupo C2', 27, 3), ('Grupo C3', 26, 3),
('Grupo D1', 35, 4), ('Grupo D2', 33, 4), ('Grupo D3', 34, 4),
('Grupo E1', 30, 5), ('Grupo E2', 30, 5), ('Grupo E3', 30, 5),
('Grupo F1', 28, 6), ('Grupo F2', 30, 6), ('Grupo F3', 30, 6),
('Grupo G1', 26, 7), ('Grupo G2', 27, 7), ('Grupo G3', 25, 7);

-- Preferencias ejemplo
INSERT INTO PreferenciaMateria (MateriaId, ProfesorId, Ranks) VALUES
(1, 1, 2), (2, 1, 1), (3, 1, 3),
(4, 2, 1), (5, 2, 2), (6, 2, 4),
(7, 3, 1), (8, 3, 3), (9, 3, 2),
(10, 4, 2), (11, 4, 1), (12, 4, 3),
(13, 5, 1), (14, 5, 2), (15, 5, 3),
(16, 6, 1), (17, 6, 2), (18, 6, 3),
(19, 7, 1), (20, 7, 2), (21, 7, 3);

-- ===================================================================
-- FIN SCRIPT
-- ===================================================================
select *from Usuario;

UPDATE Usuario SET Password = 'pbkdf2_sha256$1000000$ps6W1qAvgXDejOOFDY2AJ1$gL0uBHtoNe4/O/637TWfKgjS8UU4ViK/FrhWlHKlV/k=' WHERE Username = 'cmendoza';
UPDATE Usuario SET Password = 'pbkdf2_sha256$1000000$G6g6KeLT8r1xzKVpraHQ7g$DJ/JFHMaGBXOaxH1AHVpRnQQNVh+UVrRqLJNMbc77OA=' WHERE Username = 'ltorres';
UPDATE Usuario SET Password = 'pbkdf2_sha256$1000000$ji06Hbm2vqYb9YvrK0NVjp$ARbCFPtuFsspIwIZGdAE4qNOC2QvSb+GWH/1A7BebFA=' WHERE Username = 'arios';
UPDATE Usuario SET Password = 'pbkdf2_sha256$1000000$G8o4oysT28aMaQUaVMOPzR$Qocn8vkEcbn06LGJmZO4qHe3H7qmeFkUhF3Th/gFvOw=' WHERE Username = 'msanchez';
UPDATE Usuario SET Password = 'pbkdf2_sha256$1000000$CF89u5a5D6eiEYCCeT17Xj$v3EFvexpAJZRT5B4wGm0Xv6dy7gpok75fi04wfEgbnk=' WHERE Username = 'sgomez';
UPDATE Usuario SET Password = 'pbkdf2_sha256$1000000$qf9zuPl37A8uoMaa2jt9qx$yK9hzaTeguMiek8hBfPsnKk4Ta+Euw1XIjMTqQ4JOJk=' WHERE Username = 'jperez';
UPDATE Usuario SET Password = 'pbkdf2_sha256$1000000$ed0Cze8zCcZmVSC7AeHksi$QR8d2KQmR5sogom2IIzHx9ziRQN0DWGCHQLpXNNfaF4=' WHERE Username = 'ldiaz';
UPDATE Usuario SET Password = 'pbkdf2_sha256$1000000$kxQGA7zjDhx5xJAe59JFys$ETCPtMp3TtG8VHg2sOdbsqEVZYVxUODFQPf2Ut72DtY=' WHERE Username = 'mortega';
UPDATE Usuario SET Password = 'pbkdf2_sha256$1000000$Qlsphqe25zSzfmOUc2Kmfy$0D40v8p7B0FprGyiJcxp5TGjrbzDtQzFAJWm02IWn+M=' WHERE Username = 'evargas';

-- ===================================================================
-- CREAR USUARIO PROFESOR CON DELIMITER 
-- ===================================================================
DELIMITER //
CREATE PROCEDURE CrearUsuarioYProfesor(
    IN p_username VARCHAR(100),
    IN p_password VARCHAR(255),
    IN p_rol_id INT,
    IN p_estado_us_id INT,
    IN p_nombre VARCHAR(100),
    IN p_ap_pat VARCHAR(100),
    IN p_ap_mat VARCHAR(100),
    IN p_num_empleado VARCHAR(100),
    IN p_direccion VARCHAR(250),
    IN p_email VARCHAR(100),
    IN p_telefono VARCHAR(30),
    IN p_fecha_ingreso DATE,
    IN p_estado_id INT,
    IN p_especialidad VARCHAR(100),
    IN p_aula_id INT
)
BEGIN
    DECLARE nuevo_usuario_id INT;
    INSERT INTO Usuario (FechaAlta, Username, Password, RolId, EstadoUsId)
    VALUES (CURDATE(), p_username, p_password, p_rol_id, p_estado_us_id);
    SET nuevo_usuario_id = LAST_INSERT_ID();
    INSERT INTO Profesor (
        Nombre, ApPat, ApMat, NumEmpleado, Direccion, Email,
        Telefono, FechaIngreso, EstadoId, Especialidad, UsuarioId, AulaId
    ) VALUES (
        p_nombre, p_ap_pat, p_ap_mat, p_num_empleado, p_direccion, p_email,
        p_telefono, p_fecha_ingreso, p_estado_id, p_especialidad, nuevo_usuario_id, p_aula_id
    );
END //
DELIMITER ;
SHOW PROCEDURE STATUS WHERE Name = 'CrearUsuarioYProfesor';
CALL CrearUsuarioYProfesor(
    'rauladmin', 'pbkdf2_sha256$1000000$abc$xyz', 3, 1,
    'Raúl', 'Cuapantecatl', 'Ruiz', 'EMP123', 'Av. Universidad 123',
    'raul@example.com', '5551234567', '2025-10-19', 1, 'Ingeniería de Software', 6
);
CALL CrearUsuarioYProfesor(
    'raul1ad', 'raul123', 4, 1,
    'RAUL', 'Cuapantecatl', 'Ruiz', 'EMP123', 'Av. Universidad 123',
    'raul1@example.com', '5551234567', '2025-10-19', 1, 'Ingeniería de Software', 6
);
UPDATE Usuario SET Password = 'pbkdf2_sha256$1000000$4e6RmtXOEahWNChwiEClSd$o3knmAN+AArnOVroxNtKKdcxyPOsydMrIdrfTOnpDlg=' WHERE Username = 'rauladmin';
UPDATE Usuario SET Password = 'pbkdf2_sha256$1000000$xmFgqWNkLv8yULvSscA2f9$+76YPXUw1/PP8cdzNkgR1eVOD9qmCe+r1EfJpBQm6PA=' WHERE Username = 'raul1ad';

-- ELIMINAR DE BASE DE DATOS UN USUARIO/PROFESOR 
DROP PROCEDURE IF EXISTS BorrarUsuarioYProfesor;
DELIMITER //
CREATE PROCEDURE BorrarUsuarioYProfesor(IN p_username VARCHAR(100))
BEGIN
    DECLARE uid INT;
    -- Comparación segura con collation explícito
    SELECT Id INTO uid
    FROM Usuario
    WHERE Username = CONVERT(p_username USING utf8mb4) COLLATE utf8mb4_unicode_ci;
    -- Eliminar primero el profesor
    DELETE FROM Profesor WHERE UsuarioId = uid;
    -- Luego el usuario
    DELETE FROM Usuario WHERE Id = uid;
END //
DELIMITER ;

select *from Usuario;
select *from Profesor;
CALL BorrarUsuarioYProfesor('rauladmin');
CALL BorrarUsuarioYProfesor('raul1ad');
CALL BorrarUsuarioYProfesor('raulad');
SELECT Id, Nombre, ApPat, NumEmpleado, Email, UsuarioId FROM Profesor WHERE NumEmpleado = '9999';
SELECT Id, Username, Password, RolId FROM Usuario WHERE Username LIKE 'raul.cuapantecatl.%';

