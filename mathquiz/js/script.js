$(document).ready(function () {
    const generateQuizButton = $("#generateQuiz");
    const quizContainer = $("#quiz-container");
    const resultContainer = $("#result-container");
    const checkAnswersButton = $("#checkAnswers");
    const saveDataButton = $("#saveData");
    const tempSaveButton = $("#saveQuiz");
    const toggleFormButton = $("#toggleFormIcon");
    const formCollapse = $("#formCollapse");
    const confirmButton = $("#confirmButton");
    const kindSelect = $("#kind");
    const kindName = $("#kindName");
    const fullScreenDialog = $("#fullScreenDialog");
    const fullScreenButton = $("#fullScreenButton");
    const checkAnswersButtonDialog = $("#checkAnswersDialog");

    let questions = [];

    kindSelect.change(function () {
        kindName.text($(this).find(":selected").text());
    });

    storage.getCondition();
    let storedQuestion = storage.getQuestions(quizContainer);
    if (storedQuestion) {
        questions = storedQuestion;
    }

    generateQuizButton.click(function () {
        if (questions && questions.length > 0) {
            $('#confirmModal').modal('show');
        } else {
            generateQuiz();
        }
    });

    confirmButton.click(function () {
        generateQuiz();
        $('#confirmModal').modal('hide');
    });

    checkAnswersButton.click(function () {
        let allCorrect = true;
    
        for (let i = 0; i < questions.length; i++) {
            const userAnswer = parseInt(quizContainer.children().eq(i).find("input").val());
            const correctAnswer = questions[i].correctAnswer;
            const inputElement = quizContainer.children().eq(i).find("input");
    
            if (userAnswer !== correctAnswer) {
                allCorrect = false;
                inputElement.removeClass("is-valid");
                inputElement.addClass("is-invalid");
            } else {
                inputElement.removeClass("is-invalid");
                inputElement.addClass("is-valid");
            }
        }
    
        if (allCorrect) {
            resultContainer.addClass("text-success");
            resultContainer.removeClass("text-danger");
            resultContainer.text("Tất cả câu trả lời đều chính xác!");

            const finishModal = $("#finishModal");
            finishModal.find(".modal-body").text("Chúc mừng bạn đã hoàn thành bài kiểm tra!");
            finishModal.modal("show");

        } else {
            resultContainer.addClass("text-danger");
            resultContainer.removeClass("text-success");
            resultContainer.text("Có ít nhất một câu hỏi sai. Vui lòng kiểm tra lại.");
        }
    });

    checkAnswersButtonDialog.click(function () {
        checkAnswersButton.click();
        fullScreenDialog.modal("hide");
    });

    saveDataButton.click(function () {
        storage.storeCondition();
    });

    tempSaveButton.click(function () {
        storage.storeQuestions(questions);
    });

    toggleFormButton.click(function () {
        if (formCollapse.hasClass("show")) {
            formCollapse.removeClass("show");
            toggleFormButton.html('<span>Hiển thị điều kiện </span><i class="fas fa-chevron-down"></i>');
        } else {
            formCollapse.addClass("show");
            toggleFormButton.html('<span>Ẩn điều kiện </span><i class="fas fa-chevron-up"></i>');
        }
    });

    function generateQuiz() {
        const firstTerm = parseInt($("#firstTerm").val());
        const secondTerm = parseInt($("#secondTerm").val());
        const numQuestions = parseInt($("#numQuestions").val());
        quizContainer.empty();
        resultContainer.text("");

        if (firstTerm < 0 || secondTerm < 0) {
            resultContainer.text("Vui lòng nhập giá trị số hạng(1) (2) lớn hơn 0.");
            return;
        }

        if (numQuestions <= 0) {
            resultContainer.text("Vui lòng nhập số lượng câu hỏi hợp lệ.");
            return;
        }

        // reset all questions
        questions = [];

        const kind = $("#kind").val();
        if (kind == 'add') {
            questions = addQuiz.generate(firstTerm, secondTerm, numQuestions);
        } else if (kind == 'sub') {
            questions = subQuiz.generate(firstTerm, secondTerm, numQuestions);
        } else if (kind == 'mul') {
            questions = mulQuiz.generate(firstTerm, secondTerm, numQuestions);
        } else if (kind == 'div') {
            questions = divQuiz.generate(firstTerm, secondTerm, numQuestions);
        }

        for (let i = 0; i < numQuestions; i++) {
            const questionElement = questionElementCreator.create(questions[i], i);
            quizContainer.append(questionElement);
        }
    }

    fullScreenButton.click(function () {
        const fullScreenDialogBody = $("#fullScreenDialog .modal-body");
        const fullScreenDialogTitle = $("#fullScreenDialog .modal-title");
        const questions = $(".question-wrapper");
        const numQuestions = questions.length;
        let currentQuestion = 0;

        const changeQuestion =(index) => {
            fullScreenDialogBody.empty();
            const question = questions.eq(index).clone();
            question.find("input").addClass("w-75").removeClass("w-50");
            fullScreenDialogBody.append(question);

            const userAnswer = question.find("input");
            userAnswer.on("input", function() {
                const index = parseInt(userAnswer.attr("data-question-index"));
                questions.eq(index).find("input").val(userAnswer.val());
            });
            fullScreenDialogTitle.text(`Câu hỏi ${index + 1}/${numQuestions}`);
        }

        const showHideButtons = (index) => {
            if (index === 0) {
                $("#prevButton").hide();
                $("#nextButton").show();
            } else if (index === numQuestions - 1) {
                $("#prevButton").show();
                $("#nextButton").hide();
            } else {
                $("#prevButton").show();
                $("#nextButton").show();
            }

            if (currentQuestion === numQuestions - 1) {
                $("#exitFullscreen").hide();
                $("#checkAnswersDialog").show();
            } else {
                $("#exitFullscreen").show();
                $("#checkAnswersDialog").hide();
            }
        };

        changeQuestion(currentQuestion);
        showHideButtons(currentQuestion);

        $("#prevButton").click(function() {
            if (currentQuestion > 0) {
                currentQuestion--;
                changeQuestion(currentQuestion);
            }
            showHideButtons(currentQuestion);
        });

        $("#nextButton").click(function() {
            if (currentQuestion < numQuestions - 1) {
                currentQuestion++;
                changeQuestion(currentQuestion);
            }
            showHideButtons(currentQuestion);
        });

        fullScreenDialog.modal("show");
        fullScreenDialog.on("hidden.bs.modal", function() {
            fullScreenDialogBody.empty();
        });
    });
});
