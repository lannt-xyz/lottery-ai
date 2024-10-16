// sub.test.js
const { subQuiz } = require('../basic/sub');

describe('generate', () => {
    test('should generate the correct number of questions', () => {
        const numQuestions = 5;
        const questions = subQuiz.generate(1, 10, numQuestions);
        expect(questions.length).toBe(numQuestions);
    });

    test('should generate questions within the specified range', () => {
        const firstTerm = 1;
        const secondTerm = 10;
        const numQuestions = 5;
        const questions = subQuiz.generate(firstTerm, secondTerm, numQuestions);

        questions.forEach(question => {
            expect(question.correctAnswer).toBe(question.num1 - question.num2);
        });
    });

    test('should generate the correct number term1 and term2', () => {
        const firstTerm = 5;
        const secondTerm = 7;
        const numQuestions = 50;
        const questions = subQuiz.generate(firstTerm, secondTerm, numQuestions);

        questions.forEach(question => {
            console.log(question);
            expect(question.num1).toBeGreaterThanOrEqual(0);
            expect(question.num2).toBeGreaterThanOrEqual(0);
            if (firstTerm - secondTerm < 0) {
                expect(question.num1).toBeLessThanOrEqual(secondTerm);
                expect(question.num2).toBeLessThanOrEqual(firstTerm);
            } else {
                expect(question.num1).toBeLessThanOrEqual(firstTerm);
                expect(question.num2).toBeLessThanOrEqual(secondTerm);
            }
        });
    });
});