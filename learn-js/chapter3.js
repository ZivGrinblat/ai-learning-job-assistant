/**
 * Chapter 3 — Types, numbers, strings, truthy/falsy
 *
 * Run:  node learn-js/chapter3.js
 *
 * Read each comment block first, then the code below it.
 */

"use strict";


// =============================================================================
// EXERCISE 1 — typeof for different values
// =============================================================================
//
// typeof tells you the TYPE NAME as a string (not the value itself).
//
// Results:
//   42                    → "number"
//   3.14                  → "number"     (JS has one Number type, no int/float split)
//   "hello"               → "string"
//   true                  → "boolean"
//   undefined             → "undefined"
//   null                  → "object"     ← SURPRISING (historical bug, never fixed)
//   123n                  → "bigint"     (BigInt — integers bigger than Number.MAX_SAFE_INTEGER)
//   Symbol("id")          → "symbol"     (unique identifier, often object keys)
//   {}                    → "object"
//   []                    → "object"     ← SURPRISING (arrays ARE objects in JS)
//   function test() {}    → "function"   ← SURPRISING (functions are callable objects,
//                                              but typeof gives "function" not "object")
//
// Why typeof null === "object":
//   Old JS bug from 1995. null was stored as 0x00 internally, same tag as objects.
//   Fixing it would break old websites, so it stayed. Use `value === null` to check null.
//
// Why typeof [] === "object":
//   Arrays are special objects with numeric keys and a length property.
//   Use Array.isArray([]) when you need to detect arrays.
//
// Why typeof function === "function":
//   Functions are objects you can call, but typeof treats them specially.
//   typeof someObj === "object" — functions get their own label.

console.log("\n--- Exercise 1 ---");

console.log(typeof 42);                  // "number"
console.log(typeof 3.14);                // "number"
console.log(typeof "hello");             // "string"
console.log(typeof true);                // "boolean"
console.log(typeof undefined);           // "undefined"
console.log(typeof null);                // "object"  ← trap
console.log(typeof 123n);                 // "bigint"
console.log(typeof Symbol("id"));        // "symbol"
console.log(typeof {});                  // "object"
console.log(typeof []);                  // "object"  ← trap
console.log(typeof function test() {});  // "function" ← special case


// =============================================================================
// EXERCISE 2 — Variables and their types
// =============================================================================
//
// null         → typeof "object" (same trap as Exercise 1)
// let score;   → declared but never assigned → value is undefined, typeof "undefined"
//
// Expected output pattern:
//   Ziv string
//   31 number
//   true boolean
//   null object
//   undefined undefined

console.log("\n--- Exercise 2 ---");

const userName = "Ziv";
const age = 31;
const isStudent = true;
const middleName = null;
let score;

console.log(userName, typeof userName);
console.log(age, typeof age);
console.log(isStudent, typeof isStudent);
console.log(middleName, typeof middleName);
console.log(score, typeof score);


// =============================================================================
// EXERCISE 3 — safeDivide
// =============================================================================
//
// Division by zero in JS does NOT crash — it gives Infinity.
// This function chooses a safer contract: return null when b === 0.
// Caller can check: if (result === null) { handle error }
//
// Use === not == for zero check (strict equality).

console.log("\n--- Exercise 3 ---");

function safeDivide(a, b) {
    if (b === 0) {
        return null;
    }
    return a / b;
}

console.log(safeDivide(10, 2)); // 5
console.log(safeDivide(10, 0)); // null


// =============================================================================
// EXERCISE 4 — isValidNumber
// =============================================================================
//
// Rules:
//   - typeof value === "number"  → rejects strings like "10"
//   - NOT NaN                  → NaN is technically typeof "number" but means "invalid number"
//   - Infinity IS a number     → exercise says true for Infinity
//
// Number.isNaN(value) is safer than global isNaN() which coerces strings.

console.log("\n--- Exercise 4 ---");

function isValidNumber(value) {
    return typeof value === "number" && !Number.isNaN(value);
}

console.log(isValidNumber(10));       // true
console.log(isValidNumber(NaN));      // false
console.log(isValidNumber("10"));     // false
console.log(isValidNumber(Infinity)); // true


// =============================================================================
// EXERCISE 5 — Money precision (floating-point trap)
// =============================================================================
//
// 0.3 - 0.2 in binary floating point is NOT exactly 0.1.
// You often get 0.09999999999999998 — so === fails.
//
// Fix for money: store integers (cents), divide by 100 only for display.
// 30 cents - 20 cents === 10 cents → exact integer math.

console.log("\n--- Exercise 5 ---");

const priceA = 0.3 - 0.2;
const priceB = 0.1;

console.log(priceA);           // ~0.09999999999999998
console.log(priceB);           // 0.1
console.log(priceA === priceB); // false ← surprise!

const priceAInCents = 30 - 20;
const priceBInCents = 10;

console.log(priceAInCents);                    // 10
console.log(priceBInCents);                    // 10
console.log(priceAInCents === priceBInCents);  // true ← safe


// =============================================================================
// EXERCISE 6 — normalizeName
// =============================================================================
//
// Chain: trim() removes leading/trailing spaces, toLowerCase() normalizes case.
// Order matters: trim first so "  ZIV  " → "ZIV" → "ziv"

console.log("\n--- Exercise 6 ---");

function normalizeName(name) {
    return name.trim().toLowerCase();
}

console.log(normalizeName("  ZIV  "));   // "ziv"
console.log(normalizeName("  Anna  "));   // "anna"


// =============================================================================
// EXERCISE 7 — makeUserLabel with template literal
// =============================================================================
//
// Template literal: `text ${expression} more text`
// Like Python f-strings. ${user.name} inserts the value into the string.

console.log("\n--- Exercise 7 ---");

function makeUserLabel(user) {
    return `${user.name} (${user.age}) - ${user.role}`;
}

const user = {
    name: "Ziv",
    age: 31,
    role: "student",
};

console.log(makeUserLabel(user)); // Ziv (31) - student


// =============================================================================
// EXERCISE 8 — describeValue (truthy vs falsy)
// =============================================================================
//
// FALSY values in JavaScript (only these 8 — memorize them):
//   false, undefined, null, 0, -0, 0n, "", NaN
//
// EVERYTHING ELSE is truthy — including:
//   "false"  ← string, truthy! (non-empty string)
//   []       ← empty array, truthy! (object exists)
//   {}       ← empty object, truthy!
//
// if (value) { ... } uses this — be careful with 0 and "".

console.log("\n--- Exercise 8 ---");

function describeValue(value) {
    if (value) {
        return "truthy";
    }
    return "falsy";
}

console.log(describeValue(false));      // falsy
console.log(describeValue(undefined));  // falsy
console.log(describeValue(null));       // falsy
console.log(describeValue(0));          // falsy
console.log(describeValue(""));         // falsy
console.log(describeValue(NaN));        // falsy
console.log(describeValue("false"));    // truthy  ← trap
console.log(describeValue([]));         // truthy  ← trap
console.log(describeValue({}));         // truthy  ← trap
