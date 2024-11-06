SELECT * FROM pisos_com.propiedades_limpio;

ALTER TABLE propiedades_limpio
MODIFY COLUMN Provincia VARCHAR(100);

CREATE TABLE provincias (
    Provincia VARCHAR(100) PRIMARY KEY
);

INSERT INTO provincias (Provincia)
SELECT DISTINCT Provincia
FROM propiedades_limpio
WHERE Provincia NOT IN (SELECT Provincia FROM provincias);

ALTER TABLE propiedades_limpio
ADD CONSTRAINT fk_provincia
FOREIGN KEY (Provincia)
REFERENCES provincias(Provincia);

CREATE TABLE tipo_transaccion (
    tipo ENUM('venta', 'alquiler') PRIMARY KEY
);
INSERT INTO tipo_transaccion (tipo) VALUES ('venta'), ('alquiler');
ALTER TABLE propiedades_limpio
MODIFY COLUMN `venta/alquiler` ENUM('venta', 'alquiler');

ALTER TABLE propiedades_limpio
ADD CONSTRAINT fk_tipo_transaccion
FOREIGN KEY (`venta/alquiler`)
REFERENCES tipo_transaccion(tipo);

UPDATE propiedades_limpio
SET Precio = NULL 
WHERE Precio NOT REGEXP '^[0-9]+(\.[0-9]{1,2})?$';


UPDATE propiedades_limpio
SET Precio = REPLACE(REPLACE(Precio, '€', ''), ',', '');
UPDATE propiedades_limpio
SET Precio = TRIM(Precio);
ALTER TABLE propiedades_limpio
MODIFY COLUMN Precio INTEGER;

UPDATE propiedades_limpio
SET Timestamp = STR_TO_DATE(Timestamp, '%d/%m/%Y %H:%i');
ALTER TABLE propiedades_limpio
MODIFY COLUMN Timestamp DATETIME;

UPDATE propiedades_limpio
SET `Superficie Construida` = NULL 
WHERE `Superficie Construida` NOT REGEXP '^[0-9]+$';
UPDATE propiedades_limpio 
SET `Superficie Construida` = REPLACE(`Superficie Construida`, ' m²', '');
ALTER TABLE propiedades_limpio
MODIFY COLUMN `Superficie Construida` INTEGER;

UPDATE propiedades_limpio
SET `Superficie Útil` = NULL 
WHERE `Superficie Útil` NOT REGEXP '^[0-9]+$';
UPDATE propiedades_limpio 
SET `Superficie Útil` = REPLACE(`Superficie Útil`, ' m²', '');
ALTER TABLE propiedades_limpio
MODIFY COLUMN `Superficie Útil` INTEGER;

UPDATE propiedades_limpio
SET `Habitaciones` = NULL 
WHERE `Habitaciones` NOT REGEXP '^[0-9]+$';
ALTER TABLE propiedades_limpio
MODIFY COLUMN `Habitaciones` SMALLINT;

UPDATE propiedades_limpio
SET `Baños` = NULL 
WHERE `Baños` NOT REGEXP '^[0-9]+$';
ALTER TABLE propiedades_limpio
MODIFY COLUMN `Baños` SMALLINT;

UPDATE propiedades_limpio
SET Planta = NULL 
WHERE Planta NOT REGEXP '^[0-9]+$';
UPDATE propiedades_limpio 
SET Planta = REPLACE(Planta, 'ª', '');
ALTER TABLE propiedades_limpio
MODIFY COLUMN Planta INT;

ALTER TABLE propiedades_limpio
MODIFY COLUMN `Certificado Energético` VARCHAR(50);

UPDATE propiedades_limpio
SET `Número de fotos` = NULL 
WHERE `Número de fotos` NOT REGEXP '^[0-9]+$';
ALTER TABLE propiedades_limpio
MODIFY COLUMN `Número de fotos` SMALLINT;

ALTER TABLE propiedades_limpio
MODIFY COLUMN `Enlace` VARCHAR(255);

DESCRIBE propiedades_limpio;

CREATE TABLE certificado_energetico (
    Certificado VARCHAR(50) PRIMARY KEY
);

INSERT INTO certificado_energetico (Certificado)
SELECT DISTINCT `Certificado Energético`
FROM propiedades_limpio
WHERE `Certificado Energético` IS NOT NULL;

ALTER TABLE propiedades_limpio
ADD CONSTRAINT fk_certificado_energetico
FOREIGN KEY (`Certificado Energético`)
REFERENCES certificado_energetico(Certificado);











