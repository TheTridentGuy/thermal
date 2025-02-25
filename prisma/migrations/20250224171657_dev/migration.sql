-- CreateTable
CREATE TABLE "Scout" (
    "slack_id" TEXT NOT NULL PRIMARY KEY,
    "shiftShift_id" TEXT NOT NULL,
    CONSTRAINT "Scout_shiftShift_id_fkey" FOREIGN KEY ("shiftShift_id") REFERENCES "Shift" ("shift_id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "Shift" (
    "shift_id" TEXT NOT NULL PRIMARY KEY,
    "start" DATETIME NOT NULL,
    "end" DATETIME NOT NULL
);
