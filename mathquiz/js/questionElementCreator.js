const questionElementCreator = {
    create: function (question, index) {
        const questionElement = $("<span>").text(question.text).addClass("question");
        const answerInput = $("<input>").attr("type", "number").addClass("form-control w-50 user-answer");
        answerInput.attr("autocomplete", "off");
        answerInput.attr("name", "answer");
        answerInput.attr("data-question-index", index);
        if (question.userAnswer) {
            answerInput.val(question.userAnswer);
        }

        $(answerInput).on("focus", function () {
            $(questionElement).addClass("focus-in");
            $(questionElement).removeClass("focus-out");
        });

        $(answerInput).on("blur", function () {
            $(questionElement).addClass("focus-out");
            $(questionElement).removeClass("focus-in");
        });

        const wrapper = $("<div>").addClass("row mt-3 question-wrapper d-flex align-items-center"); 
        const questionWrapper = $("<div>").addClass("col-md-6 col-6 text-end");
        questionWrapper.append(questionElement);
        const answerWrapper = $("<div>").addClass("col-md-6 col-6 text-start");
        answerWrapper.append(answerInput);
        wrapper.append(questionWrapper);
        wrapper.append(answerWrapper);

        return wrapper;
    }
};