// div.test.js
const { divQuiz } = require('../basic/div');

describe('generate', () => {
    test('should generate the correct number of questions', () => {
        const numQuestions = 5;
        const questions = divQuiz.generate(1, 10, numQuestions);
        expect(questions.length).toBe(numQuestions);
    });

    test('should generate questions within the specified range', () => {
        const firstTerm = 1;
        const secondTerm = 10;
        const numQuestions = 5;
        const questions = divQuiz.generate(firstTerm, secondTerm, numQuestions);

        questions.forEach(question => {
            expect(question.correctAnswer).toBe(question.num1 / question.num2);
        });
    });

    test('should generate the correct number term1 and term2', () => {
        const firstTerm = 5;
        const secondTerm = 7;
        const numQuestions = 50;
        const questions = divQuiz.generate(firstTerm, secondTerm, numQuestions);

        questions.forEach(question => {
            console.log(question);
            expect(question.num1).toBeGreaterThanOrEqual(0);
            expect(question.num2).toBeGreaterThanOrEqual(0);
            expect(question.num1).toBeGreaterThanOrEqual(question.num2);
            expect(question.num1 % question.num2).toBe(0);
        });
    });
});