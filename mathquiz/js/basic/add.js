function generate(firstTerm, secondTerm, numQuestions) {
    let questions = [];

    for (let i = 0; i < numQuestions; i++) {
        const num1 = Math.floor(Math.random() * (firstTerm + 1));
        const num2 = Math.floor(Math.random() * (secondTerm + 1));
        const correctAnswer = num1 + num2;

        const text = `${num1} + ${num2} = `;
        questions.push({ num1, num2, text, correctAnswer });
    }

    return questions;
}

var addQuiz = {
    generate: generate
}

module.exports = { addQuiz };
