function generate(firstTerm, secondTerm, numQuestions) {
    let questions = [];

    // generate the math questions with divisions and the result must be integer, and if the result must be geater than 1
    for (let i = 0; i < numQuestions; i++) {
        let dividend = Math.floor(Math.random() * (secondTerm + 1));
        while (dividend === 0) {
            dividend = Math.floor(Math.random() * (secondTerm + 1));
        }

        let divisor = 0;
        while (divisor / dividend < 2) {
            divisor = dividend * Math.floor(Math.random() * (firstTerm + 1));
        }

        let correctAnswer = divisor / dividend;

        const text = `${divisor} : ${dividend} = `;
        const num1 = divisor;
        const num2 = dividend;
        questions.push({ num1, num2, text, correctAnswer });
    }

    return questions;
}

var divQuiz = {
    generate: generate
}

module.exports = { divQuiz };
