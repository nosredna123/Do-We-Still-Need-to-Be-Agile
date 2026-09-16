/*
  Warnings:

  - You are about to drop the column `file_path` on the `Material` table. All the data in the column will be lost.
  - Added the required column `bucket_path` to the `Material` table without a default value. This is not possible if the table is not empty.
  - Added the required column `public_url` to the `Material` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Material" DROP COLUMN "file_path",
ADD COLUMN     "bucket_path" TEXT NOT NULL,
ADD COLUMN     "public_url" TEXT NOT NULL;
