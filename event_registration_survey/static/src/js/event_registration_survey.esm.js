/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";
import {resizeTextArea} from "@web/core/utils/autoresize";
import {utils as uiUtils} from "@web/core/ui/ui_service";
import {Interaction} from "@web/public/interaction";
import {ModalRegistration} from "@website_event/interactions/modal_registration";

function resetErrors(rootEl) {
  rootEl.querySelectorAll(".o_survey_question_error").forEach((el) => {
    el.replaceChildren();
    el.classList.remove("slide_in");
  });
  rootEl
    .querySelectorAll(".o_survey_error")
    .forEach((el) => el.classList.add("d-none"));
  rootEl.querySelectorAll(".o_survey_question_matrix th.bg-danger").forEach((row) => {
    row.classList.remove("bg-danger");
  });
}

function showErrors(rootEl, errors) {
  for (const [key, message] of Object.entries(errors || {})) {
    const questionWrapperEl = rootEl.querySelector(`#${CSS.escape(key)}`);
    const errorEl = questionWrapperEl?.querySelector(".o_survey_question_error");
    if (errorEl) {
      const span = document.createElement("span");
      span.textContent = message;
      errorEl.appendChild(span);
      errorEl.classList.add("slide_in");
    }
  }
}

function collectFormValues(formEl) {
  const values = {};
  formEl.querySelectorAll("input, select, textarea").forEach((inputEl) => {
    const name = inputEl.getAttribute("name");
    if (!name) {
      return;
    }
    const type = inputEl.getAttribute("type");
    if (type === "checkbox") {
      if (!values[name]) {
        values[name] = [];
      }
      if (inputEl.checked) {
        values[name].push(inputEl.value);
      }
    } else if (type === "radio") {
      if (inputEl.checked) {
        values[name] = inputEl.value;
      }
    } else {
      values[name] = inputEl.value;
    }
  });
  return values;
}

function isRequiredQuestionAnswered(questionWrapperEl) {
  // Skip hidden conditional questions
  if (questionWrapperEl.classList.contains("d-none")) {
    return true;
  }

  const questionTypeEl = questionWrapperEl.querySelector("[data-question-type]");
  const questionType = questionTypeEl?.dataset.questionType;
  // Counter/question-id/survey-id are rendered as separate data attributes
  // by question_container (event_templates.xml) specifically so callers
  // don't have to parse them back out of a combined string like the
  // wrapper's own id ("{counter}-{question.id}-{survey.id}") - matrix row
  // inputs are named "{counter}-{question.id}_{row.id}-{survey.id}" (the
  // row id is spliced in the middle, not appended at the end), so those
  // three pieces need to be reassembled around the row id, not just
  // string-glued using the wrapper id or the table's data-name.
  const counter = questionWrapperEl.dataset.counter;
  const questionId = questionWrapperEl.dataset.questionId;
  const surveyId = questionWrapperEl.dataset.surveyId;

  const hasNonEmptyValue = (selector) =>
    Array.from(questionWrapperEl.querySelectorAll(selector))
      .filter((el) => !el.disabled)
      .some((el) => String(el.value || "").trim() !== "");

  switch (questionType) {
    case "simple_choice_radio":
      return (
        questionWrapperEl.querySelectorAll('input[type="radio"]:checked').length > 0
      );

    case "multiple_choice":
      return (
        questionWrapperEl.querySelectorAll('input[type="checkbox"]:checked').length > 0
      );

    case "matrix": {
      const tableEl = questionWrapperEl.querySelector("table");
      const subQuestions = tableEl
        ? JSON.parse(tableEl.dataset.subQuestions || "[]")
        : [];
      for (const subQuestionId of subQuestions) {
        const rowName = `${counter}-${questionId}_${subQuestionId}-${surveyId}`;
        const hasChecked =
          questionWrapperEl.querySelector(
            `input[name="${CSS.escape(rowName)}"]:checked`
          ) !== null;
        if (!hasChecked) {
          const rowHeaderEl = questionWrapperEl.querySelector(
            `.o_survey_question_matrix tbody tr[id="${subQuestionId}"] > th`
          );
          rowHeaderEl?.classList.add("bg-danger");
          return false;
        }
      }
      return true;
    }

    case "char_box":
    case "text_box":
      return hasNonEmptyValue("input[type='text'], input[type='email'], textarea");

    case "numerical_box":
      return hasNonEmptyValue("input[type='number']");

    case "date":
    case "datetime":
      return hasNonEmptyValue("input");

    default:
      // Unrecognized/unsupported question type (the server-side
      // template renders a warning instead of real inputs for these,
      // see question_container in event_templates.xml) - fall back to
      // a generic "some input has a value" check.
      if (!questionType) {
        console.warn(
          "event_registration_survey: question has no recognized " +
            "data-question-type, see question_container's fallback " +
            "warning for unsupported survey question types",
          questionWrapperEl
        );
      }
      return Array.from(questionWrapperEl.querySelectorAll("input, textarea, select"))
        .filter((el) => !el.disabled)
        .some((el) => {
          const type = (el.getAttribute("type") || "").toLowerCase();
          if (type === "radio" || type === "checkbox") {
            return el.checked;
          }
          return String(el.value || "").trim() !== "";
        });
  }
}

patch(ModalRegistration.prototype, {
  /**
   * @param {SubmitEvent} ev
   */
  async onSubmit(ev) {
    const formEl = ev.currentTarget;
    const surveyQuestionDivEl = formEl.querySelector('[name="survey_question_div"]');

    if (!surveyQuestionDivEl) {
      return super.onSubmit(ev);
    }

    resetErrors(formEl);
    const errors = {};

    formEl.querySelectorAll('[data-required="True"]').forEach((questionWrapperEl) => {
      if (!isRequiredQuestionAnswered(questionWrapperEl)) {
        errors[questionWrapperEl.getAttribute("id")] =
          questionWrapperEl.dataset.constrErrorMsg;
      }
    });

    if (Object.keys(errors).length) {
      ev.preventDefault();
      // Core's legacy public_root.js also listens for "submit" on any
      // ".js_website_submit_form" (delegated on the document), and
      // permanently disables the submit button with a spinner icon
      // regardless of preventDefault, on the assumption that the page
      // is about to navigate away. Stop the event from bubbling that
      // far so it never runs when the submission is actually
      // rejected, or the button is stuck disabled with no way to
      // retry.
      ev.stopPropagation();
      showErrors(formEl, errors);
      return;
    }

    const submitValues = collectFormValues(formEl);
    if (Object.keys(submitValues).length) {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = "post-data";
      input.value = JSON.stringify(submitValues);
      formEl.appendChild(input);
    }

    return super.onSubmit(ev);
  },
});

export class SurveyRegistrationQuestions extends Interaction {
  static selector = "#modal_attendees_registration [name='survey_question_div']";
  dynamicContent = {
    _root: {
      "t-on-click": this.onClick,
    },
  };

  setup() {
    // Embedded server-side by event_registration_attendee_details_template.xml
    // (mirrors how survey.survey_fill_form embeds its own
    // data-triggered-questions-by-answer attribute) - read once per
    // attendee, since each attendee gets its own interaction instance
    // and its own copy of this data attribute.
    try {
      this.conditionalQuestionInfo = JSON.parse(
        this.el.dataset.conditionalQuestionInfo || "{}"
      );
    } catch (err) {
      console.error(
        "event_registration_survey: failed to parse conditional question info",
        err
      );
      this.conditionalQuestionInfo = {};
    }
  }

  start() {
    this.el.querySelectorAll("textarea").forEach((el) => resizeTextArea(el));

    // Both the "selected" and "unselected" icons are always rendered by
    // the server template (event_templates.xml), and only one of the
    // two is meant to be visible - core relies on a CSS rule scoped
    // under ".o_survey_background" to do that, which this embedded
    // modal doesn't have as an ancestor, so it has to be done in JS
    // instead (see updateRadioIcons/updateCheckboxIcons/updateMatrixIcons).
    // That JS only runs reactively on click, so it must also run once
    // here for every choice, or all of them show both icons at once
    // until the user interacts with them.
    this.el.querySelectorAll(".o_survey_matrix_btn").forEach((matrixBtnEl) => {
      const inputEl = matrixBtnEl.querySelector("input");
      const isSelected = Boolean(inputEl?.checked);
      this.updateMatrixIcons(matrixBtnEl, isSelected);
      if (isSelected) {
        matrixBtnEl.classList.add("o_survey_selected");
      }
    });

    this.el.querySelectorAll(".o_survey_choice_btn").forEach((labelEl) => {
      const inputEl = labelEl.querySelector(
        "input[type='radio'], input[type='checkbox']"
      );
      if (!inputEl) {
        return;
      }
      if (inputEl.type === "radio") {
        this.updateRadioIcons(inputEl, inputEl.checked);
      } else {
        this.updateCheckboxIcons(inputEl, inputEl.checked);
      }
      if (inputEl.checked) {
        labelEl.classList.add("o_survey_selected");
      }
    });

    if (!uiUtils.isSmall()) {
      const firstTextInputEl = this.el
        .querySelector(".js_question-wrapper")
        ?.querySelector("input[type='text'],input[type='number'],textarea");
      if (
        firstTextInputEl?.classList.contains("form-control") &&
        !firstTextInputEl.classList.contains("o_survey_comment")
      ) {
        firstTextInputEl.focus();
      }
    }
  }

  onClick(ev) {
    const matrixBtnEl = ev.target.closest(".o_survey_matrix_btn");
    if (matrixBtnEl) {
      this.onMatrixBtnClick(matrixBtnEl);
      return;
    }
    const radioEl = ev.target.closest('input[type="radio"]');
    if (radioEl) {
      this.onRadioChoiceClick(radioEl);
      return;
    }
    const checkboxEl = ev.target.closest('input[type="checkbox"]');
    if (checkboxEl) {
      this.onCheckboxChoiceClick(checkboxEl);
    }
  }

  onCheckboxChoiceClick(checkboxEl) {
    this.updateCheckboxIcons(checkboxEl, checkboxEl.checked);
  }

  updateCheckboxIcons(targetEl, isSelected) {
    const labelEl = targetEl.closest("label");
    // Note: toggling the "d-none" class rather than the "hidden"
    // property - FontAwesome's ".fa" class sets "display: inline-block"
    // as an author-stylesheet rule, which wins over the UA stylesheet's
    // "[hidden] { display: none }" regardless of selector specificity,
    // so "hidden" alone would silently fail to hide these <i> icons.
    // Bootstrap's ".d-none" uses "!important", so it always wins.
    labelEl
      ?.querySelectorAll("i.fa-check-square, i.fa-square-o")
      .forEach((el) => el.classList.add("d-none"));
    labelEl
      ?.querySelector(isSelected ? "i.fa-check-square" : "i.fa-square-o")
      ?.classList.remove("d-none");
  }

  onRadioChoiceClick(targetEl) {
    const nameValue = targetEl.getAttribute("name");
    const radioGroup = this.el.querySelectorAll(
      `input[type="radio"][name="${CSS.escape(nameValue)}"]`
    );

    if (targetEl.classList.contains("o_survey_form_choice_item_selected")) {
      targetEl.checked = false;
      targetEl.classList.remove("o_survey_form_choice_item_selected");
      this.updateRadioIcons(targetEl, false);
      targetEl.dispatchEvent(new Event("change"));
      this.toggleRelatedQuestionVisibility(targetEl, "off");
      return;
    }

    radioGroup.forEach((radioEl) => {
      this.updateRadioIcons(radioEl, false);
      radioEl.classList.remove("o_survey_form_choice_item_selected");
      if (radioEl !== targetEl) {
        this.toggleRelatedQuestionVisibility(radioEl, "off");
      }
    });

    targetEl.classList.add("o_survey_form_choice_item_selected");
    this.updateRadioIcons(targetEl, true);
    targetEl.dispatchEvent(new Event("change"));
    this.toggleRelatedQuestionVisibility(targetEl, "on");
  }

  updateRadioIcons(targetEl, isSelected) {
    const labelEl = targetEl.closest("label");
    labelEl
      ?.querySelectorAll("i.fa-check-circle, i.fa-times-circle, i.fa-circle-thin")
      .forEach((el) => el.classList.add("d-none"));
    labelEl
      ?.querySelector(isSelected ? "i.fa-check-circle" : "i.fa-circle-thin")
      ?.classList.remove("d-none");
  }

  onMatrixBtnClick(targetEl) {
    const inputEl = targetEl.querySelector("input");
    if (!inputEl) {
      return;
    }

    if (inputEl.type === "radio") {
      this.el
        .querySelectorAll(`input[type="radio"][name="${CSS.escape(inputEl.name)}"]`)
        .forEach((radioEl) => {
          this.updateMatrixIcons(radioEl.closest("td"), false);
          radioEl.checked = false;
        });
    }

    inputEl.checked = !inputEl.checked;
    inputEl.dispatchEvent(new Event("change"));
    this.updateMatrixIcons(targetEl, inputEl.checked);
  }

  updateMatrixIcons(targetEl, isSelected) {
    targetEl
      .querySelectorAll(
        "i.fa-check-square, i.fa-check-circle, i.fa-square-o, i.fa-circle-thin"
      )
      .forEach((el) => el.classList.add("d-none"));
    const selectors = isSelected
      ? "i.fa-check-square, i.fa-check-circle"
      : "i.fa-square-o, i.fa-circle-thin";
    targetEl.querySelectorAll(selectors).forEach((el) => el.classList.remove("d-none"));
  }

  /**
   * Show or hide the related questions of a simple choice answer that was
   * selected with a radio button click.
   *
   * @param {HTMLElement} targetEl radio button element
   * @param {"on"|"off"} mode whether to show or hide the related question
   */
  toggleRelatedQuestionVisibility(targetEl, mode) {
    const selectedQuestionAnswerValue = targetEl.value;
    const questionWrapperEl = targetEl.closest(".js_question-wrapper");
    const relatedCounter = questionWrapperEl?.dataset.counter;
    let relatedSurveyId = questionWrapperEl?.dataset.surveyId;

    if (!relatedSurveyId) {
      return;
    }
    relatedSurveyId = relatedSurveyId.toString();

    const surveyInfo = this.conditionalQuestionInfo[relatedSurveyId];
    const questionIdsToTrigger =
      surveyInfo?.triggered_questions_by_answer[selectedQuestionAnswerValue];
    if (!questionIdsToTrigger) {
      return;
    }

    for (const questionIdToTrigger of questionIdsToTrigger) {
      const toggledId = `${relatedCounter}-${questionIdToTrigger}-${relatedSurveyId}`;
      const relatedQuestionWrapperEl = this.el.querySelector(
        `#${CSS.escape(toggledId)}`
      );
      relatedQuestionWrapperEl?.classList.toggle("d-none", mode !== "on");
    }
  }
}

registry
  .category("public.interactions")
  .add(
    "event_registration_survey.survey_registration_questions",
    SurveyRegistrationQuestions
  );
