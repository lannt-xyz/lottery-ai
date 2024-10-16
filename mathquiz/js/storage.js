const storage = {
    getCondition: function () {
        const savedData = localStorage.getItem("quizData");
        if (savedData) {
            const { kind, firstTerm, secondTerm, numQuestions } = JSON.parse(savedData);
            $("#kind").val(kind);
            $("#kind").trigger("change");
            $("#firstTerm").val(firstTerm);
            $("#secondTerm").val(secondTerm);
            $("#numQuestions").val(numQuestions);
        }
    },
    storeCondition: function () {
        const kind = $("#kind").val();
        const firstTerm = $("#firstTerm").val();
        const secondTerm = $("#secondTerm").val();
        const numQuestions = $("#numQuestions").val();

        const dataToSave = JSON.stringify({ kind, firstTerm, secondTerm, numQuestions });
        localStorage.setItem("quizData", dataToSave);

        const alertModal = $("#alertModal");
        alertModal.find(".modal-body").text("Dữ liệu đã được lưu vào Local Storage!");
        alertModal.modal("show");
    },
    getQuestions: function (quizContainer) {
        const savedQuestions = localStorage.getItem('questions');
        if (!savedQuestions) {
            return
        }

        const questions = JSON.parse(savedQuestions);
        questions.forEach((question, index) => {
            const questionElement = questionElementCreator.create(question, index);
            quizContainer.append(questionElement);
        });

        return questions;
    },
    storeQuestions: function (questions) {
        // with each question, we need to get the answer and the user's answer due to getting data of the input class `user-answer`
        questions.forEach((question, index) => {
            // find the input element with the class `user-answer` and get the data attribute `question-index`, and it's value is the index of the question
            const userAnswer = $(`.user-answer[data-question-index=${index}]`).val();
            question.userAnswer = userAnswer;
        });
        localStorage.setItem('questions', JSON.stringify(questions));

        const alertModal = $("#alertModal");
        alertModal.find(".modal-body").text("Dữ liệu đã được lưu vào Local Storage!");
        alertModal.modal("show");
    },
};
