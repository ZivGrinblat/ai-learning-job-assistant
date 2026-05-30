// const result = function factorial(n) {
//     let product = 1;

//     while(n > 1)
//         product *= n--;

//     return product;
// }

// console.log(result(5));


// class Point {
//     constructor(x, y) {
//         this.x = x;
//         this.y = y;
//     }

//     distance() {
//         return Math.sqrt(this.x * this.x + this.y * this.y);
//     }
// }

// const p = new Point(1, 5);
// console.log(p.distance());

console.log("I am learning JavaScript seriously.");

const name = "Ziv";
const age = 31;
const isStudent = true;

if (isStudent)
    console.log(`My name is ${name} and I am ${age} years old, and I am a student!`);
else 
    console.log(`My name is ${name} and I am ${age} years old, and I am not a student!`);



// =============================================================================
// Task A — Book as a plain object (not a class)
// =============================================================================

const book = {
    title: "My Life",
    author: "Saadat",
    pages: 350,
    isFinished: false,
};

book.year = 1950;

console.log(book);

// =============================================================================
// Task B — sumNumbers as a standalone function
// =============================================================================

function sumNumbers(numbers) {
    let sum = 0;
    for (const num of numbers) {
        sum += num;
    }
    return sum;
}

const nums_for_example = [5, 6, 78, 123, 11, 1];
console.log(sumNumbers(nums_for_example));

const biggerThanTheLimit = function(nums, limitNumber) 
    {
    if (nums.length === 0) {
        return []
    }
    const aboveTheLimit = [];
    for (const num of nums) {
        if (num > limitNumber)
            aboveTheLimit.push(num);
    }

    return aboveTheLimit;
}

console.log(biggerThanTheLimit([5, 6, 78, 123, 11, 1], 10));


const students = [
    { name: "Anna", grade: 85 },
    { name: "Boris", grade: 72 },
    { name: "Clara", grade: 91 }
  ];

const getBestStudent = function(students) {
    let bestStudent = students[0];
    for (const student of students) {
        if(student.grade > bestStudent.grade)
            bestStudent = student;
    }
    return bestStudent;
}
console.log(getBestStudent(students));

const rectangle = {
    width: 10,
    height: 5, 

    area() {
        return this.width * this.height;
    },

    perimeter() {
        return 2 * (this.width + this.height);
    }
};

console.log(rectangle.area());      // 50
console.log(rectangle.perimeter()); // 30


// =============================================================================
// Task C — BankAccount (methods return true/false; print outside the class)
// =============================================================================

class BankAccount {
    constructor(owner, balance) {
        this.owner = owner;
        this.balance = balance;
    }

    deposit(amount) {
        if (amount <= 0) {
            return false;
        }
        this.balance += amount;
        return true;
    }

    withdraw(amount) {
        if (amount <= 0) {
            return false;
        }
        if (amount > this.balance) {
            return false;
        }
        this.balance -= amount;
        return true;
    }

    getBalance() {
        return this.balance;
    }
}

const account = new BankAccount("Ziv", 100);

if (account.deposit(50)) {
    console.log(`Deposit OK. Balance: ${account.getBalance()}`);
} else {
    console.log("Deposit failed.");
}

if (account.withdraw(70)) {
    console.log(`Withdraw OK. Balance: ${account.getBalance()}`);
} else {
    console.log("Withdraw failed.");
}

if (account.withdraw(200)) {
    console.log(`Withdraw OK. Balance: ${account.getBalance()}`);
} else {
    console.log("Withdraw failed.");
    console.log(`Balance unchanged: ${account.getBalance()}`);
}


// =============================================================================
// Task D — countCharacters (lowercase, ignore spaces)
// =============================================================================

function countCharacters(text) {
    const charCount = {};
    const lower = text.toLowerCase();

    for (const char of lower) {
        if (char === " ") {
            continue;
        }
        charCount[char] = (charCount[char] || 0) + 1;
    }

    return charCount;
}

console.log(countCharacters("Hello Hello"));
console.log(countCharacters("JavaScript"));
