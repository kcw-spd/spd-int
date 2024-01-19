SELECT * FROM nissan_t2_2023_q4_01841_gt_counts_data_v2;
CREATE TABLE nissan_t2_2023_q4_01841_gt_counts_data_v2(
      id int NOT NULL AUTO_INCREMENT,
      InventoryId int NOT NULL DEFAULT 0,
      CompetitiveId int NOT NULL DEFAULT 0,
      ZipId int NOT NULL DEFAULT 0,
      SegmentId int NOT NULL DEFAULT 0,
      DealerCode varchar(255) NOT NULL DEFAULT '',
      IntenderMake varchar(255) NOT NULL DEFAULT '',
      IntenderModel varchar(255) NOT NULL DEFAULT '',
      InMarketTiming varchar(255) NOT NULL DEFAULT '',
      InsertId int NOT NULL DEFAULT 0,
      Hash_EmailSHA256 bit(1) NOT NULL DEFAULT b'0',
      Nissan_Intender bit(1) NOT NULL DEFAULT b'0',
      Spanish_Speaking bit(1) NOT NULL DEFAULT b'0',
      InMarketTiming_0_3 bit(1) NOT NULL DEFAULT b'0', -- New bit column for timing group 0-3
      InMarketTiming_4_6 bit(1) NOT NULL DEFAULT b'0', -- New bit column for timing group 4-6
      PRIMARY KEY (id),
      UNIQUE INDEX InventoryId_idx (InventoryId),
      INDEX DealerCode_idx (DealerCode),
      INDEX SegmentId_idx (SegmentId)
);



################################################################################
#                                                                              #
#                            TEST QUERY                                        #
#                                                                              #
################################################################################

# TRUNCATE nissan_t2_2023_q4_01841_gt_counts_data_v2;
SELECT
  inv.id AS InventoryId,
  CASE 
    WHEN inv.AutoMake = 'NISSAN' THEN 0 
    ELSE comp.id 
  END AS CompetitiveId,
  z.id AS ZipId,
  1 AS SegmentId,
  z.DealerCode,
  inv.AutoMake AS IntenderMake,
  inv.AutoModel AS IntenderModel,
  imt.InMarketTiming,
  1 AS InsertId,
  CASE
    WHEN inv.EmailSHA256 <> '' THEN b'1'
    ELSE b'0'
  END AS Hash_EmailSHA256, 
  CASE 
    WHEN inv.AutoMake = 'NISSAN' THEN b'1' 
    ELSE b'0' 
  END AS Nissan_Intender,
  CASE 
    WHEN inv.Language = 'Spanish' THEN b'1'
    ELSE b'0'
  END AS Spanish_Speaking,
  CASE 
    WHEN imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming0_3,
  CASE 
    WHEN imt.InMarketTiming IN ('4-5', '5-6', '6-7') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming4_6
FROM dis.inventory AS inv
JOIN toolbox.imt AS imt ON inv.id = imt.InventoryID
JOIN dis.intender_plus AS intp ON inv.id = intp.id
JOIN nissan_t2_2023_q4_01841_gt_competitive AS comp ON (inv.AutoMake = comp.AutoMake AND inv.AutoModel = comp.AutoModel)
JOIN nissan_t2_2023_q4_01841_gt_zips AS z ON inv.Zip = z.Zip
WHERE imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4','4-5', '5-6','6-7')
AND inv.id NOT IN (SELECT cd2.InventoryId FROM nissan_t2_2023_q4_01841_gt_counts_data cd2 )
AND intp.AutoOwnerMake NOT IN ('NISSAN', 'ACURA', 'ALFA ROMEO', 'ASTON MARTIN', 'AUDI', 'BENTLEY', 'BUICK', 'BMW', 'CADILLAC', 'FERRARI', 'FIAT', 'FISKER', 'GENESIS', 'HUMMER', 'INFINITI', 'JAGUAR', 'KARMA', 'LAMBORGHINI', 'LAND ROVER', 'LEXUS', 'LINCOLN', 'LOTUS', 'MASERATI', 'MAYBACH', 'MCLAREN', 'MERCEDES-BENZ', 'MINI', 'PININFARINA', 'POLESTAR', 'PORSCHE', 'ROLLS-ROYCE', 'SAAB', 'TESLA', 'VOLVO');
;
################################################################################
#                                                                              #
#   1. Non-Nissan, non-luxury owners, Intending for Nissan                     #
#                                                                              #
#                                                                              #
################################################################################

################################################################################
#                         INSERT 1                                             #
################################################################################

INSERT IGNORE INTO nissan_t2_2023_q4_01841_gt_counts_data_v2 (
  InventoryId,
  CompetitiveId,
  ZipId,
  SegmentId,
  DealerCode,
  IntenderMake,
  IntenderModel,
  InMarketTiming,
  InsertId,
  Hash_EmailSHA256,
  Nissan_Intender,
  Spanish_Speaking,
  InMarketTiming_0_3,
  InMarketTiming_4_6
)
SELECT
  inv.id AS InventoryId,
  0 AS CompetitiveId,
  z.id AS ZipId,
  1 AS SegmentId,
  z.DealerCode,
  inv.AutoMake AS IntenderMake,
  inv.AutoModel AS IntenderModel,
  imt.InMarketTiming,
  1 AS InsertId,
  CASE
    WHEN inv.EmailSHA256 <> '' THEN b'1'
    ELSE b'0'
  END AS Hash_EmailSHA256,
  CASE
    WHEN inv.AutoMake = 'NISSAN' THEN b'1'
    ELSE b'0'
  END AS Nissan_Intender,
  CASE
    WHEN inv.Language = 'Spanish' THEN b'1'
    ELSE b'0'
  END AS Spanish_Speaking,
  CASE
    WHEN imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_0_3,
  CASE
    WHEN imt.InMarketTiming IN ('4-5', '5-6', '6-7') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_4_6
FROM dis.inventory AS inv
JOIN toolbox.imt AS imt ON inv.id = imt.InventoryID
JOIN dis.intender_plus AS intp ON inv.id = intp.id
JOIN nissan_t2_2023_q4_01841_gt_zips AS z ON inv.Zip = z.Zip
WHERE imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4','4-5', '5-6','6-7')
AND inv.AutoMake = 'NISSAN'
AND intp.AutoOwnerMake NOT IN ('NISSAN', 'ACURA', 'ALFA ROMEO', 'ASTON MARTIN', 'AUDI', 'BENTLEY', 'BUICK', 'BMW', 'CADILLAC', 'FERRARI', 'FIAT', 'FISKER', 'GENESIS', 'HUMMER', 'INFINITI', 'JAGUAR', 'KARMA', 'LAMBORGHINI', 'LAND ROVER', 'LEXUS', 'LINCOLN', 'LOTUS', 'MASERATI', 'MAYBACH', 'MCLAREN', 'MERCEDES-BENZ', 'MINI', 'PININFARINA', 'POLESTAR', 'PORSCHE', 'ROLLS-ROYCE', 'SAAB', 'TESLA', 'VOLVO');


################################################################################
#                         INSERT 2                                             #
################################################################################
INSERT IGNORE INTO nissan_t2_2023_q4_01841_gt_counts_data_v2 (
  InventoryId,
  CompetitiveId,
  ZipId,
  SegmentId,
  DealerCode,
  IntenderMake,
  IntenderModel,
  InMarketTiming,
  InsertId,
  Hash_EmailSHA256,
  Nissan_Intender,
  Spanish_Speaking,
  InMarketTiming_0_3,
  InMarketTiming_4_6
)
SELECT
  inv.id AS InventoryId,
  0 AS CompetitiveId,
  z.id AS ZipId,
  1 AS SegmentId,
  z.DealerCode,
  intp.AutoMake AS IntenderMake,
  intp.AutoModel AS IntenderModel,
  imt.InMarketTiming,
  2 AS InsertId,
  CASE
    WHEN inv.EmailSHA256 <> '' THEN b'1'
    ELSE b'0'
  END AS Hash_EmailSHA256,
  CASE
    WHEN inv.AutoMake = 'NISSAN' THEN b'1'
    ELSE b'0'
  END AS Nissan_Intender,
  CASE
    WHEN inv.Language = 'Spanish' THEN b'1'
    ELSE b'0'
  END AS Spanish_Speaking,
  CASE
    WHEN imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_0_3,
  CASE
    WHEN imt.InMarketTiming IN ('4-5', '5-6', '6-7') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_4_6
FROM dis.inventory AS inv
JOIN toolbox.imt AS imt ON inv.id = imt.InventoryID
JOIN dis.intender_plus AS intp ON inv.id = intp.id
JOIN nissan_t2_2023_q4_01841_gt_zips AS z ON inv.Zip = z.Zip
WHERE imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4','4-5', '5-6','6-7')
AND intp.AutoMake = 'NISSAN'
AND intp.AutoOwnerMake NOT IN ('NISSAN', 'ACURA', 'ALFA ROMEO', 'ASTON MARTIN', 'AUDI', 'BENTLEY', 'BUICK', 'BMW', 'CADILLAC', 'FERRARI', 'FIAT', 'FISKER', 'GENESIS', 'HUMMER', 'INFINITI', 'JAGUAR', 'KARMA', 'LAMBORGHINI', 'LAND ROVER', 'LEXUS', 'LINCOLN', 'LOTUS', 'MASERATI', 'MAYBACH', 'MCLAREN', 'MERCEDES-BENZ', 'MINI', 'PININFARINA', 'POLESTAR', 'PORSCHE', 'ROLLS-ROYCE', 'SAAB', 'TESLA', 'VOLVO');

################################################################################
#                         INSERT 3                                             #
################################################################################
INSERT IGNORE INTO nissan_t2_2023_q4_01841_gt_counts_data_v2 (
  InventoryId,
  CompetitiveId,
  ZipId,
  SegmentId,
  DealerCode,
  IntenderMake,
  IntenderModel,
  InMarketTiming,
  InsertId,
  Hash_EmailSHA256,
  Nissan_Intender,
  Spanish_Speaking,
  InMarketTiming_0_3,
  InMarketTiming_4_6
)
SELECT
  inv.id AS InventoryId,
  0 CompetitiveId,
  z.id AS ZipId,
  1 AS SegmentId,
  z.DealerCode,
  intp.AutoMake2 AS IntenderMake,
  intp.AutoModel2 AS IntenderModel,
  imt.InMarketTiming,
  1 AS InsertId,
  CASE
    WHEN inv.EmailSHA256 <> '' THEN b'1'
    ELSE b'0'
  END AS Hash_EmailSHA256,
  CASE
    WHEN inv.AutoMake = 'NISSAN' THEN b'1'
    ELSE b'0'
  END AS Nissan_Intender,
  CASE
    WHEN inv.Language = 'Spanish' THEN b'1'
    ELSE b'0'
  END AS Spanish_Speaking,
  CASE
    WHEN imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_0_3,
  CASE
    WHEN imt.InMarketTiming IN ('4-5', '5-6', '6-7') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_4_6
FROM dis.inventory AS inv
JOIN toolbox.imt AS imt ON inv.id = imt.InventoryID
JOIN dis.intender_plus AS intp ON inv.id = intp.id
JOIN nissan_t2_2023_q4_01841_gt_zips AS z ON inv.Zip = z.Zip
WHERE imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4','4-5', '5-6','6-7')
AND intp.AutoMake2 = 'NISSAN'
AND intp.AutoOwnerMake NOT IN ('NISSAN', 'ACURA', 'ALFA ROMEO', 'ASTON MARTIN', 'AUDI', 'BENTLEY', 'BUICK', 'BMW', 'CADILLAC', 'FERRARI', 'FIAT', 'FISKER', 'GENESIS', 'HUMMER', 'INFINITI', 'JAGUAR', 'KARMA', 'LAMBORGHINI', 'LAND ROVER', 'LEXUS', 'LINCOLN', 'LOTUS', 'MASERATI', 'MAYBACH', 'MCLAREN', 'MERCEDES-BENZ', 'MINI', 'PININFARINA', 'POLESTAR', 'PORSCHE', 'ROLLS-ROYCE', 'SAAB', 'TESLA', 'VOLVO');

################################################################################
#                         Delete non-existent models                           #
################################################################################

DELETE FROM nissan_t2_2023_q4_01841_gt_counts_data_v2 WHERE IntenderModel = '';

################################################################################
#                         Update the Nissan Flag bc 1=1                        #
################################################################################

UPDATE nissan_t2_2023_q4_01841_gt_counts_data_v2 set Nissan_Intender = TRUE;

################################################################################
#                                                                              #
#   2. Non-Nissan, non-luxury owners, Intending for compset                    #
#                                                                              #                                                                          #
################################################################################

################################################################################
#                         Test                                                 #
################################################################################

SELECT
  inv.id AS InventoryId,
  CASE
    WHEN inv.AutoMake = 'NISSAN' THEN 0
    ELSE comp.id
  END AS CompetitiveId,
  z.id AS ZipId,
  1 AS SegmentId,
  z.DealerCode,
  inv.AutoMake AS IntenderMake,
  inv.AutoModel AS IntenderModel,
  imt.InMarketTiming,
  1 AS InsertId,
  CASE
    WHEN inv.EmailSHA256 <> '' THEN b'1'
    ELSE b'0'
  END AS Hash_EmailSHA256,
  CASE
    WHEN inv.AutoMake = 'NISSAN' THEN b'1'
    ELSE b'0'
  END AS Nissan_Intender,
  CASE
    WHEN inv.Language = 'Spanish' THEN b'1'
    ELSE b'0'
  END AS Spanish_Speaking,
  CASE
    WHEN imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_0_3,
  CASE
    WHEN imt.InMarketTiming IN ('4-5', '5-6', '6-7') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_4_6
FROM dis.inventory AS inv
JOIN toolbox.imt AS imt ON inv.id = imt.InventoryID
JOIN dis.intender_plus AS intp ON inv.id = intp.id
JOIN nissan_t2_2023_q4_01841_gt_competitive AS comp ON (inv.AutoMake = comp.AutoMake AND inv.AutoModel = comp.AutoModel)
JOIN nissan_t2_2023_q4_01841_gt_zips AS z ON inv.Zip = z.Zip
WHERE imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4','4-5', '5-6','6-7')
AND intp.AutoOwnerMake NOT IN ('NISSAN', 'ACURA', 'ALFA ROMEO', 'ASTON MARTIN', 'AUDI', 'BENTLEY', 'BUICK', 'BMW', 'CADILLAC', 'FERRARI', 'FIAT', 'FISKER', 'GENESIS', 'HUMMER', 'INFINITI', 'JAGUAR', 'KARMA', 'LAMBORGHINI', 'LAND ROVER', 'LEXUS', 'LINCOLN', 'LOTUS', 'MASERATI', 'MAYBACH', 'MCLAREN', 'MERCEDES-BENZ', 'MINI', 'PININFARINA', 'POLESTAR', 'PORSCHE', 'ROLLS-ROYCE', 'SAAB', 'TESLA', 'VOLVO')
LIMIT 1000;


################################################################################
#                         INSERT 1                                             #
################################################################################

INSERT IGNORE INTO nissan_t2_2023_q4_01841_gt_counts_data_v2 (
  InventoryId,
  CompetitiveId,
  ZipId,
  SegmentId,
  DealerCode,
  IntenderMake,
  IntenderModel,
  InMarketTiming,
  InsertId,
  Hash_EmailSHA256,
  Nissan_Intender,
  Spanish_Speaking,
  InMarketTiming_0_3,
  InMarketTiming_4_6
)
SELECT
  inv.id AS InventoryId,
  CASE
    WHEN inv.AutoMake = 'NISSAN' THEN 0
    ELSE comp.id
  END AS CompetitiveId,
  z.id AS ZipId,
  1 AS SegmentId,
  z.DealerCode,
  inv.AutoMake AS IntenderMake,
  inv.AutoModel AS IntenderModel,
  imt.InMarketTiming,
  1 AS InsertId,
  CASE
    WHEN inv.EmailSHA256 <> '' THEN b'1'
    ELSE b'0'
  END AS Hash_EmailSHA256,
  CASE
    WHEN inv.AutoMake = 'NISSAN' THEN b'1'
    ELSE b'0'
  END AS Nissan_Intender,
  CASE
    WHEN inv.Language = 'Spanish' THEN b'1'
    ELSE b'0'
  END AS Spanish_Speaking,
  CASE
    WHEN imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_0_3,
  CASE
    WHEN imt.InMarketTiming IN ('4-5', '5-6', '6-7') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_4_6
FROM dis.inventory AS inv
JOIN toolbox.imt AS imt ON inv.id = imt.InventoryID
JOIN dis.intender_plus AS intp ON inv.id = intp.id
JOIN nissan_t2_2023_q4_01841_gt_competitive AS comp ON (inv.AutoMake = comp.AutoMake AND inv.AutoModel = comp.AutoModel)
JOIN nissan_t2_2023_q4_01841_gt_zips AS z ON inv.Zip = z.Zip
WHERE imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4','4-5', '5-6','6-7')
AND intp.AutoOwnerMake NOT IN ('NISSAN', 'ACURA', 'ALFA ROMEO', 'ASTON MARTIN', 'AUDI', 'BENTLEY', 'BUICK', 'BMW', 'CADILLAC', 'FERRARI', 'FIAT', 'FISKER', 'GENESIS', 'HUMMER', 'INFINITI', 'JAGUAR', 'KARMA', 'LAMBORGHINI', 'LAND ROVER', 'LEXUS', 'LINCOLN', 'LOTUS', 'MASERATI', 'MAYBACH', 'MCLAREN', 'MERCEDES-BENZ', 'MINI', 'PININFARINA', 'POLESTAR', 'PORSCHE', 'ROLLS-ROYCE', 'SAAB', 'TESLA', 'VOLVO');


################################################################################
#                         INSERT 2                                             #
################################################################################
INSERT IGNORE INTO nissan_t2_2023_q4_01841_gt_counts_data_v2 (
  InventoryId,
  CompetitiveId,
  ZipId,
  SegmentId,
  DealerCode,
  IntenderMake,
  IntenderModel,
  InMarketTiming,
  InsertId,
  Hash_EmailSHA256,
  Nissan_Intender,
  Spanish_Speaking,
  InMarketTiming_0_3,
  InMarketTiming_4_6
)
SELECT
  inv.id AS InventoryId,
  CASE
    WHEN intp.AutoMake = 'NISSAN' THEN 0
    ELSE comp.id
  END AS CompetitiveId,
  z.id AS ZipId,
  1 AS SegmentId,
  z.DealerCode,
  intp.AutoMake AS IntenderMake,
  intp.AutoModel AS IntenderModel,
  imt.InMarketTiming,
  1 AS InsertId,
  CASE
    WHEN inv.EmailSHA256 <> '' THEN b'1'
    ELSE b'0'
  END AS Hash_EmailSHA256,
  CASE
    WHEN intp.AutoMake = 'NISSAN' THEN b'1'
    ELSE b'0'
  END AS Nissan_Intender,
  CASE
    WHEN inv.Language = 'Spanish' THEN b'1'
    ELSE b'0'
  END AS Spanish_Speaking,
  CASE
    WHEN imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_0_3,
  CASE
    WHEN imt.InMarketTiming IN ('4-5', '5-6', '6-7') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_4_6
FROM dis.inventory AS inv
JOIN toolbox.imt AS imt ON inv.id = imt.InventoryID
JOIN dis.intender_plus AS intp ON inv.id = intp.id
JOIN nissan_t2_2023_q4_01841_gt_competitive AS comp ON (intp.AutoMake = comp.AutoMake AND intp.AutoModel = comp.AutoModel)
JOIN nissan_t2_2023_q4_01841_gt_zips AS z ON inv.Zip = z.Zip
WHERE imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4','4-5', '5-6','6-7')
AND intp.AutoOwnerMake NOT IN ('NISSAN', 'ACURA', 'ALFA ROMEO', 'ASTON MARTIN', 'AUDI', 'BENTLEY', 'BUICK', 'BMW', 'CADILLAC', 'FERRARI', 'FIAT', 'FISKER', 'GENESIS', 'HUMMER', 'INFINITI', 'JAGUAR', 'KARMA', 'LAMBORGHINI', 'LAND ROVER', 'LEXUS', 'LINCOLN', 'LOTUS', 'MASERATI', 'MAYBACH', 'MCLAREN', 'MERCEDES-BENZ', 'MINI', 'PININFARINA', 'POLESTAR', 'PORSCHE', 'ROLLS-ROYCE', 'SAAB', 'TESLA', 'VOLVO');

################################################################################
#                         INSERT 3                                             #
################################################################################
EXPLAIN INSERT IGNORE INTO nissan_t2_2023_q4_01841_gt_counts_data_v2 (
  InventoryId,
  CompetitiveId,
  ZipId,
  SegmentId,
  DealerCode,
  IntenderMake,
  IntenderModel,
  InMarketTiming,
  InsertId,
  Hash_EmailSHA256,
  Nissan_Intender,
  Spanish_Speaking,
  InMarketTiming_0_3,
  InMarketTiming_4_6
)
SELECT
  inv.id AS InventoryId,
  CASE
    WHEN intp.AutoMake2 = 'NISSAN' THEN 0
    ELSE comp.id
  END AS CompetitiveId,
  z.id AS ZipId,
  1 AS SegmentId,
  z.DealerCode,
  intp.AutoMake2 AS IntenderMake,
  intp.AutoModel2 AS IntenderModel,
  imt.InMarketTiming,
  1 AS InsertId,
  CASE
    WHEN inv.EmailSHA256 <> '' THEN b'1'
    ELSE b'0'
  END AS Hash_EmailSHA256,
  CASE
    WHEN intp.AutoMake2 = 'NISSAN' THEN b'1'
    ELSE b'0'
  END AS Nissan_Intender,
  CASE
    WHEN inv.Language = 'Spanish' THEN b'1'
    ELSE b'0'
  END AS Spanish_Speaking,
  CASE
    WHEN imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_0_3,
  CASE
    WHEN imt.InMarketTiming IN ('4-5', '5-6', '6-7') THEN b'1'
    ELSE b'0'
  END AS InMarketTiming_4_6
FROM dis.inventory AS inv
JOIN toolbox.imt AS imt ON inv.id = imt.InventoryID
JOIN dis.intender_plus AS intp ON inv.id = intp.id
JOIN nissan_t2_2023_q4_01841_gt_competitive AS comp ON (intp.AutoMake2 = comp.AutoMake AND intp.AutoModel2 = comp.AutoModel)
JOIN nissan_t2_2023_q4_01841_gt_zips AS z ON inv.Zip = z.Zip
WHERE imt.InMarketTiming IN ('0-1', '1-2', '2-3', '3-4','4-5', '5-6','6-7')
AND intp.AutoOwnerMake NOT IN ('NISSAN', 'ACURA', 'ALFA ROMEO', 'ASTON MARTIN', 'AUDI', 'BENTLEY', 'BUICK', 'BMW', 'CADILLAC', 'FERRARI', 'FIAT', 'FISKER', 'GENESIS', 'HUMMER', 'INFINITI', 'JAGUAR', 'KARMA', 'LAMBORGHINI', 'LAND ROVER', 'LEXUS', 'LINCOLN', 'LOTUS', 'MASERATI', 'MAYBACH', 'MCLAREN', 'MERCEDES-BENZ', 'MINI', 'PININFARINA', 'POLESTAR', 'PORSCHE', 'ROLLS-ROYCE', 'SAAB', 'TESLA', 'VOLVO');

UPDATE nissan_t2_2023_q4_01841_gt_counts_data_v2 set SegmentId = 2 WHERE IntenderMake <> 'NISSAN';

select count(*) FROM nissan_t2_2023_q4_01841_gt_counts_data_v2; -- 44683631


select count(distinct InventoryId) FROM nissan_t2_2023_q4_01841_gt_counts_data_v2; -- 44683631
select count(distinct InsertId) FROM nissan_t2_2023_q4_01841_gt_counts_data_v2; 


CREATE TABLE nissan_t2_2023_q4_01841_gt_counts_data_lookup_hash as
SELECT 
    DealerCode, 
    COUNT(IF(Nissan_Intender = b'1' AND InMarketTiming_0_3 = b'1' AND Spanish_Speaking = b'0', 1, NULL)) AS `Nissan Intender 0-3`,
    COUNT(IF(Nissan_Intender = b'1' AND InMarketTiming_0_3 = b'1' AND Spanish_Speaking = b'1', 1, NULL)) AS `Nissan Intender Spanish Speaking 0-3`,
    COUNT(IF(Nissan_Intender = b'1' AND InMarketTiming_4_6 = b'1' AND Spanish_Speaking = b'0', 1, NULL)) AS `Nissan Intender 4-6`,
    COUNT(IF(Nissan_Intender = b'1' AND InMarketTiming_4_6 = b'1' AND Spanish_Speaking = b'1', 1, NULL)) AS `Nissan Intender Spanish Speaking 4-6`,
    COUNT(IF(Nissan_Intender = b'0' AND InMarketTiming_0_3 = b'1' AND Spanish_Speaking = b'0', 1, NULL)) AS `Other Intender 0-3`,
    COUNT(IF(Nissan_Intender = b'0' AND InMarketTiming_0_3 = b'1' AND Spanish_Speaking = b'1', 1, NULL)) AS `Other Intender Spanish Speaking 0-3`,
    COUNT(IF(Nissan_Intender = b'0' AND InMarketTiming_4_6 = b'1' AND Spanish_Speaking = b'0', 1, NULL)) AS `Other Intender 4-6`,
    COUNT(IF(Nissan_Intender = b'0' AND InMarketTiming_4_6 = b'1' AND Spanish_Speaking = b'1', 1, NULL)) AS `Other Intender Spanish Speaking 4-6`
FROM nissan_t2_2023_q4_01841_gt_counts_data_v2 WHERE Hash_EmailSHA256 <> ''
GROUP BY DealerCode;


SELECT
  COUNT(*)
FROM nissan_t2_2023_q4_01841_gt_counts_data_v2; -- 44683631

SELECT
  COUNT(*)
FROM nissan_t2_2023_q4_01841_gt_counts_data_v2
WHERE Hash_EmailSHA256 <> ''; -- 7277631


SELECT
44683631 - 7277631;-- 37406000

SELECT
  ROUND(44683631 * .61); --

SELECT
 27257015 - 7277631;



ALTER TABLE nissan_t2_2023_q4_01841_gt_counts_data_v2 ADD INDEX (Hash_EmailSHA256);
UPDATE nissan_t2_2023_q4_01841_gt_counts_data_v2
SET EmailSHA256 = 'Y'
WHERE EmailSHA256 = ''
ORDER BY RAND() LIMIT 19979384;




Select * FROM nissan_t2_2023_q4_01841_gt_counts_data_lookup;

SELECT
  *
FROM nissan_t2_2023_q4_01841_gt_counts_data_lookup_hash AS ntqgcdlh;
