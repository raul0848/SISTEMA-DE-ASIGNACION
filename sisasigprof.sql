-- 1. Crear la base de datos
-- DROP DATABASE IF EXISTS sisasigprof;
CREATE DATABASE sisasigprof;
use sisasigprof;

-- Tabla Usuario
CREATE TABLE Usuario (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(100),
    Email VARCHAR(100) UNIQUE,
    Rol VARCHAR(50)
);

-- Tabla RolesPermisos
CREATE TABLE RolesPermisos (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(50)
);

-- Tabla Profesor
CREATE TABLE Profesor (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(100),
    Especialidad VARCHAR(100),
    UsuarioId INT,
    FOREIGN KEY (UsuarioId) REFERENCES Usuario(Id)
);

-- Tabla Materia
CREATE TABLE Materia (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(100),
    Codigo VARCHAR(20),
    ProfesorId INT,
    FOREIGN KEY (ProfesorId) REFERENCES Profesor(Id)
);

-- Tabla Horario
CREATE TABLE Horario (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Dia VARCHAR(15),
    HorarioInicio TIME,
    HoraFin TIME
);

-- Tabla MateriaHorario (relación muchos a muchos)
CREATE TABLE MateriaHorario (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    MateriaId INT,
    HorarioId INT,
    FOREIGN KEY (MateriaId) REFERENCES Materia(Id),
    FOREIGN KEY (HorarioId) REFERENCES Horario(Id)
);

-- Tabla EmailServicios (servicio de envío de correo)
CREATE TABLE EmailServicios (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Destino VARCHAR(100),
    Mensaje TEXT
);

-- Tabla PushServicios (servicio de notificaciones push)
CREATE TABLE PushServicios (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    UsuarioId INT,
    Mensaje TEXT,
    FOREIGN KEY (UsuarioId) REFERENCES Usuario(Id)
);

-- Tabla GeneradorReportes
CREATE TABLE GeneradorReportes (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Contenido TEXT
);

-- Tabla RegistroEventos
CREATE TABLE RegistroEventos (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Descripcion TEXT,
    Fecha DATE,
    GeneradorReporteId INT,
    FOREIGN KEY (GeneradorReporteId) REFERENCES GeneradorReportes(Id)
);

-- Tabla RegistroVisitas
CREATE TABLE RegistroVisitas (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Usuario VARCHAR(100),
    FechaEntrada DATETIME,
    FechaSalida DATETIME,
    GeneradorReporteId INT,
    FOREIGN KEY (GeneradorReporteId) REFERENCES GeneradorReportes(Id)
);

-- Tabla Administrador (Extendido desde Usuario con rol 'Administrador')
CREATE TABLE Administrador (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    UsuarioId INT UNIQUE,
    FOREIGN KEY (UsuarioId) REFERENCES Usuario(Id)
);

-- Tabla Grupo
CREATE TABLE Grupo (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(100),
    ProfesorId INT,
    FOREIGN KEY (ProfesorId) REFERENCES Profesor(Id)
);

-- Tabla PreferenciaMateria
CREATE TABLE PreferenciaMateria (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    ProfesorId INT,
    MateriaId INT,
    PreferenciaNivel INT, -- Nivel del 1 (alta) al 5 (baja)
    FOREIGN KEY (ProfesorId) REFERENCES Profesor(Id),
    FOREIGN KEY (MateriaId) REFERENCES Materia(Id)
);

-- Tabla MateriaGrupo (relación entre materias y grupos)
CREATE TABLE MateriaGrupo (
    Id INT PRIMARY KEY AUTO_INCREMENT,
    MateriaId INT,
    GrupoId INT,
    FOREIGN KEY (MateriaId) REFERENCES Materia(Id),
    FOREIGN KEY (GrupoId) REFERENCES Grupo(Id)
);

CREATE TABLE Login (
    UsuarioId INT PRIMARY KEY,
    Usuario VARCHAR(100) UNIQUE,
    Contrasena VARCHAR(100),
    FOREIGN KEY (UsuarioId) REFERENCES Usuario(Id)
);

-- Insertar usuarios (2 admins y 7 profesores)
INSERT INTO Usuario (Nombre, Email, Rol) VALUES
('Carlos Mendoza', 'carlos.mendoza@example.com', 'Administrador'),
('Lucía Torres', 'lucia.torres@example.com', 'Administrador'),
('Ana Ríos', 'ana.rios@example.com', 'Profesor'),
('Mario Sánchez', 'mario.sanchez@example.com', 'Profesor'),
('Sandra Gómez', 'sandra.gomez@example.com', 'Profesor'),
('José Pérez', 'jose.perez@example.com', 'Profesor'),
('Laura Díaz', 'laura.diaz@example.com', 'Profesor'),
('Miguel Ortega', 'miguel.ortega@example.com', 'Profesor'),
('Elena Vargas', 'elena.vargas@example.com', 'Profesor');

-- Insertar credenciales ficticias
INSERT INTO Login (UsuarioId, Usuario, Contrasena) VALUES
(1, 'admin1', 'admin123'),
(2, 'admin2', 'admin123'),
(3, 'ana.rios', 'prof123'),
(4, 'mario.sanchez', 'prof123'),
(5, 'sandra.gomez', 'prof123'),
(6, 'jose.perez', 'prof123'),
(7, 'laura.diaz', 'prof123'),
(8, 'miguel.ortega', 'prof123'),
(9, 'elena.vargas', 'prof123');

INSERT INTO Profesor (Nombre, Especialidad, UsuarioId) VALUES
('Ana Ríos', 'Matemáticas', 3),
('Mario Sánchez', 'Física', 4),
('Sandra Gómez', 'Biología', 5),
('José Pérez', 'Historia', 6),
('Laura Díaz', 'Lengua y Literatura', 7),
('Miguel Ortega', 'Informática', 8),
('Elena Vargas', 'Química', 9);

-- Profesor 1
INSERT INTO Materia (Nombre, Codigo, ProfesorId) VALUES
('Álgebra Lineal', 'MAT101', 1),
('Cálculo Diferencial', 'MAT102', 1),
('Estadística', 'MAT103', 1),

-- Profesor 2
('Física I', 'FIS101', 2),
('Electromagnetismo', 'FIS102', 2),
('Física Moderna', 'FIS103', 2),

-- Profesor 3
('Biología General', 'BIO101', 3),
('Anatomía Humana', 'BIO102', 3),
('Ecología', 'BIO103', 3),

-- Profesor 4
('Historia Universal', 'HIS101', 4),
('Historia de México', 'HIS102', 4),
('Ciencias Sociales', 'HIS103', 4),

-- Profesor 5
('Literatura Clásica', 'LEN101', 5),
('Redacción y Estilo', 'LEN102', 5),
('Análisis Literario', 'LEN103', 5),

-- Profesor 6
('Programación I', 'INF101', 6),
('Bases de Datos', 'INF102', 6),
('Redes de Computadoras', 'INF103', 6),

-- Profesor 7
('Química General', 'QUI101', 7),
('Química Orgánica', 'QUI102', 7),
('Laboratorio de Química', 'QUI103', 7);

INSERT INTO Horario (Dia, HorarioInicio, HoraFin) VALUES
('Lunes', '08:00:00', '09:00:00'),
('Lunes', '09:00:00', '10:00:00'),
('Lunes', '10:00:00', '11:00:00'),
('Martes', '08:00:00', '09:00:00'),
('Martes', '09:00:00', '10:00:00'),
('Martes', '10:00:00', '11:00:00'),
('Miércoles', '08:00:00', '09:00:00'),
('Miércoles', '09:00:00', '10:00:00'),
('Miércoles', '10:00:00', '11:00:00'),
('Jueves', '08:00:00', '09:00:00'),
('Jueves', '09:00:00', '10:00:00'),
('Jueves', '10:00:00', '11:00:00'),
('Viernes', '08:00:00', '09:00:00'),
('Viernes', '09:00:00', '10:00:00'),
('Viernes', '10:00:00', '11:00:00'),
('Lunes', '11:00:00', '12:00:00'),
('Martes', '11:00:00', '12:00:00'),
('Miércoles', '11:00:00', '12:00:00'),
('Jueves', '11:00:00', '12:00:00'),
('Viernes', '11:00:00', '12:00:00'),
('Lunes', '12:00:00', '13:00:00');

INSERT INTO MateriaHorario (MateriaId, HorarioId) VALUES
(1, 1), (2, 2), (3, 3),
(4, 4), (5, 5), (6, 6),
(7, 7), (8, 8), (9, 9),
(10, 10), (11, 11), (12, 12),
(13, 13), (14, 14), (15, 15),
(16, 16), (17, 17), (18, 18),
(19, 19), (20, 20), (21, 21);

-- 3 grupos por profesor
INSERT INTO Grupo (Nombre, ProfesorId) VALUES
('Grupo A1', 1), ('Grupo A2', 1), ('Grupo A3', 1),
('Grupo B1', 2), ('Grupo B2', 2), ('Grupo B3', 2),
('Grupo C1', 3), ('Grupo C2', 3), ('Grupo C3', 3),
('Grupo D1', 4), ('Grupo D2', 4), ('Grupo D3', 4),
('Grupo E1', 5), ('Grupo E2', 5), ('Grupo E3', 5),
('Grupo F1', 6), ('Grupo F2', 6), ('Grupo F3', 6),
('Grupo G1', 7), ('Grupo G2', 7), ('Grupo G3', 7);

INSERT INTO MateriaGrupo (MateriaId, GrupoId) VALUES
(1, 1), (2, 2), (3, 3),
(4, 4), (5, 5), (6, 6),
(7, 7), (8, 8), (9, 9),
(10, 10), (11, 11), (12, 12),
(13, 13), (14, 14), (15, 15),
(16, 16), (17, 17), (18, 18),
(19, 19), (20, 20), (21, 21);

INSERT INTO PreferenciaMateria (ProfesorId, MateriaId, PreferenciaNivel) VALUES
(1, 1, 2), (1, 2, 1), (1, 3, 3),
(2, 4, 1), (2, 5, 2), (2, 6, 4),
(3, 7, 1), (3, 8, 3), (3, 9, 2),
(4, 10, 2), (4, 11, 1), (4, 12, 3),
(5, 13, 1), (5, 14, 2), (5, 15, 3),
(6, 16, 1), (6, 17, 2), (6, 18, 3),
(7, 19, 1), (7, 20, 2), (7, 21, 3);

select *from Usuario;
select *from Login;