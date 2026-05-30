/**
 * Chapter 2 — Syntax, formatting, naming, and traps
 *
 * Run:  node learn-js/chapter2.js
 *
 * Each section matches one exercise from the chapter.
 * Read the comment block FIRST, then the code below it.
 */


// =============================================================================
// EXERCISE 1 — Valid or invalid identifiers?
// =============================================================================
//
// Rules in JavaScript:
//   - Identifiers can use letters, digits, _, and $ (not at start for digits)
//   - First character must be a letter, _, or $
//   - Hyphens (-) are NOT allowed — JS reads them as minus operator
//   - Some words are "reserved" (class, return, if…) — cannot use alone as names
//
// userName    VALID   — starts with letter, camelCase is normal style
// _userName   VALID   — _ at start is allowed (often "internal" convention)
// $user        VALID   — $ at start is allowed (jQuery uses this pattern)
// 2users      INVALID — cannot START with a digit
// user-name   INVALID — hyphen is minus: user - name, not one identifier
// class       INVALID — reserved word (used for class declarations)
// className   VALID   — "class" + "Name" together is fine; only bare "class" is reserved
// first_name  VALID   — underscore inside is fine (snake_case)
// firstName   VALID   — camelCase, very common in JS
//
// No runnable code for this exercise — it's a reading/checklist exercise.


// =============================================================================
// EXERCISE 2 — Rewrite with good formatting, semicolons, and braces
// =============================================================================
//
// Problems in the original:
//   - No semicolons (optional in JS but good habit while learning)
//   - No spaces around = and >= (hard to read)
//   - if/else bodies on same line without braces — works for one line but
//     easy to break when you add a second line; braces make intent clear
//
// Good habit: always use braces on if/else even for one statement.

console.log("\n--- Exercise 2 ---");

const name = "Ziv";
const age = 31;

if (age >= 18) {
    console.log("adult");
} else {
    console.log("minor");
}


// =============================================================================
// EXERCISE 3 — What will this print?
// =============================================================================
//
// JavaScript is CASE-SENSITIVE.
// "name" and "Name" are TWO DIFFERENT variables — different letters, different boxes.
//
// Prints:
//   Ziv
//   David
//
// NOT two "Ziv" or two "David". Capital N matters.

console.log("\n--- Exercise 3 ---");

const nameEx3 = "Ziv";   // renamed to avoid clash with Exercise 2's `name`
const Name = "David";

console.log(nameEx3);  // Ziv
console.log(Name);     // David


// =============================================================================
// EXERCISE 4 — The "return line-break" trap
// =============================================================================
//
// WRONG version:
//
//   function createUser() {
//     return
//     {
//       name: "Ziv",
//       age: 31
//     };
//   }
//
// What happens:
//   JS inserts a semicolon after `return` because of Automatic Semicolon Insertion (ASI).
//   So it becomes:  return;   ← returns undefined immediately
//   The { name: "Ziv", ... } block is dead code — never reached as a return value.
//
// FIX: put { on the SAME line as return, or wrap in parentheses.

console.log("\n--- Exercise 4 ---");

function createUser() {
    return {
        name: "Ziv",
        age: 31,
    };
}

console.log(createUser());  // { name: 'Ziv', age: 31 }


// =============================================================================
// EXERCISE 5 — Fix forEach formatting
// =============================================================================
//
// Original worked but was hard to read:
//   - Missing semicolons after array and closing });
//   - Bad indentation inside the callback
//
// Arrow function (number) => { ... } is the callback — runs once per array item.

console.log("\n--- Exercise 5 ---");

const numbers = [1, 2, 3];

numbers.forEach((number) => {
    console.log(number);
});


// =============================================================================
// EXERCISE 6 — Bad naming: Student vs student
// =============================================================================
//
// Problems:
//   1. Same letters, different case — easy to confuse Student vs student
//   2. Student (capital S) looks like a CLASS name in JS convention
//   3. const Student = "Ziv" — a string labeled like a type; misleading
//   4. student = object — now you have two unrelated things that look related
//
// JS convention:
//   - PascalCase (Student) → classes / constructors
//   - camelCase (studentName, currentStudent) → variables / values
//
// Better names below: role vs data are clearly different.

console.log("\n--- Exercise 6 ---");

const studentName = "Ziv";
const currentStudent = { name: "David" };

console.log(studentName);
console.log(currentStudent);


// =============================================================================
// EXERCISE 7 — Improve comments (remove noise, keep useful ones)
// =============================================================================
//
// Bad comments restate the code ("Subtract amount from balance" above `balance - amount`).
// Good comments explain WHY or non-obvious rules.
//
// Here the useful fact: invalid withdraw returns balance UNCHANGED (not an error throw).

console.log("\n--- Exercise 7 ---");

function withdraw(balance, amount) {
    // Reject withdraws larger than balance — caller keeps original balance
    if (amount > balance) {
        return balance;
    }

    return balance - amount;
}

console.log(withdraw(100, 30));  // 70
console.log(withdraw(100, 150)); // 100 — unchanged


// =============================================================================
// EXERCISE 8 — isValidVariableName (simplified rules, no regex)
// =============================================================================
//
// Algorithm:
//   1. Empty string → false
//   2. Check reserved words list → false if match
//   3. First char must be letter, _, or $
//   4. Rest of chars must be letter, digit, _, or $
//   5. Hyphen (-) fails at step 4
//
// Helper: isLetter, isDigit, isAllowedChar — keeps loops readable.

console.log("\n--- Exercise 8 ---");

const RESERVED_WORDS = ["class", "return", "if", "else", "for", "while"];

function isLetter(char) {
    return (
        (char >= "a" && char <= "z") ||
        (char >= "A" && char <= "Z")
    );
}

function isDigit(char) {
    return char >= "0" && char <= "9";
}

function isValidFirstChar(char) {
    return isLetter(char) || char === "_" || char === "$";
}

function isValidRestChar(char) {
    return isLetter(char) || isDigit(char) || char === "_" || char === "$";
}

function isValidVariableName(name) {
    if (name.length === 0) {
        return false;
    }

    if (RESERVED_WORDS.includes(name)) {
        return false;
    }

    if (!isValidFirstChar(name[0])) {
        return false;
    }

    for (let i = 1; i < name.length; i++) {
        if (!isValidRestChar(name[i])) {
            return false;
        }
    }

    return true;
}

console.log(isValidVariableName("userName"));  // true
console.log(isValidVariableName("2users"));    // false
console.log(isValidVariableName("class"));     // false
console.log(isValidVariableName("_count"));    // true
console.log(isValidVariableName("user-name")); // false


// =============================================================================
// EXERCISE 9 — Rewrite getResult (return trap + formatting)
// =============================================================================
//
// Same trap as Exercise 4:
//
//   return
//   "excellent"
//
// becomes `return;` — function returns undefined, not "excellent".
//
// Also fixed: consistent braces, spacing, semicolons.

console.log("\n--- Exercise 9 ---");

function getResult(score) {
    if (score > 90) {
        return "excellent";
    } else if (score > 70) {
        return "good";
    } else {
        return "needs work";
    }
}

console.log(getResult(95));  // excellent
