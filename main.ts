// Deliver the finished front page to the grader's output folder.
//
// This entry ships its image as entry.png beside this file. This program's
// job is deliberately small: confirm the file really is the PNG we expect,
// then place an exact copy at <output>/entry.png. Both grading runs execute
// the same steps, so both runs land identical bytes.

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// A PNG always opens with these eight bytes.
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1024 * 1024;
const MAX_SIDE = 1024;

function repoRoot(): string {
  return dirname(fileURLToPath(import.meta.url));
}

function outputFolder(): string {
  const given = process.env.MAKEFUN_OUTPUT_DIR;
  return given !== undefined && given.length > 0 ? given : "/output";
}

function pngDimensions(bytes: Buffer): { width: number; height: number } {
  // Layout of a PNG head: 8-byte signature, then the IHDR chunk. The width
  // sits at bytes 16..19 and the height at 20..23, both big-endian.
  if (bytes.length < 24 || !bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    throw new Error("entry.png does not open with a PNG signature");
  }
  // The first chunk after the signature must be IHDR; its four type bytes
  // sit at 12..15. Anything else is not a PNG image, whatever its first
  // eight bytes claim.
  if (!bytes.subarray(12, 16).equals(Buffer.from("IHDR", "ascii"))) {
    throw new Error("entry.png has no IHDR chunk after its signature");
  }
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
}

function main(): void {
  const source = join(repoRoot(), "entry.png");
  const payload = readFileSync(source);

  if (payload.length > MAX_BYTES) {
    throw new Error(
      `entry.png is ${payload.length} bytes, over the ${MAX_BYTES} byte cap`,
    );
  }
  const { width, height } = pngDimensions(payload);
  if (width > MAX_SIDE || height > MAX_SIDE) {
    throw new Error(
      `entry.png is ${width}x${height}, over the ${MAX_SIDE}x${MAX_SIDE} cap`,
    );
  }

  const folder = outputFolder();
  mkdirSync(folder, { recursive: true });
  const target = join(folder, "entry.png");
  copyFileSync(source, target);

  // Prove the copy landed byte for byte before reporting success.
  const written = readFileSync(target);
  if (!written.equals(payload)) {
    throw new Error("the copy at the output path does not match entry.png");
  }
  const digest = createHash("sha256").update(payload).digest("hex");
  console.log(
    `entry.png ${width}x${height}, ${payload.length} bytes, sha256 ${digest} -> ${target}`,
  );
}

main();
