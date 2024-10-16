function generate(firstTerm, secondTerm, numQuestions) {
    let questions = [];

    // generate the math questions with subtractions
    for (let i = 0; i < numQuestions; i++) {
        let num1 = Math.floor(Math.random() * (firstTerm + 1));
        let num2 = Math.floor(Math.random() * (secondTerm + 1));
        let correctAnswer = num1 - num2;

        // if correctAnswer is negative, swap num1 and num2
        if (correctAnswer < 0) {
            const temp = num1;
            num1 = num2;
            num2 = temp;
            correctAnswer = num1 - num2;
        }

        const text = `${num1} - ${num2} = `;
        questions.push({ num1, num2, text, correctAnswer });
    }

    return questions;
}

var subQuiz = {
    generate: generate
}

module.exports = { subQuiz };
