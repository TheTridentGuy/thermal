-- CreateTable
CREATE TABLE "Scout" (
    "slack_id" TEXT NOT NULL PRIMARY KEY
);

-- CreateTable
CREATE TABLE "Shift" (
    "shift_id" TEXT NOT NULL PRIMARY KEY,
    "start" DATETIME NOT NULL,
    "end" DATETIME NOT NULL
);

-- CreateTable
CREATE TABLE "_ScoutToShift" (
    "A" TEXT NOT NULL,
    "B" TEXT NOT NULL,
    CONSTRAINT "_ScoutToShift_A_fkey" FOREIGN KEY ("A") REFERENCES "Scout" ("slack_id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "_ScoutToShift_B_fkey" FOREIGN KEY ("B") REFERENCES "Shift" ("shift_id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateIndex
CREATE UNIQUE INDEX "_ScoutToShift_AB_unique" ON "_ScoutToShift"("A", "B");

-- CreateIndex
CREATE INDEX "_ScoutToShift_B_index" ON "_ScoutToShift"("B");
