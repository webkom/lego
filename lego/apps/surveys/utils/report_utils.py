import base64
import io

import matplotlib
from matplotlib.ticker import MultipleLocator

from lego.apps.surveys.constants import TEXT_FIELD
from lego.apps.surveys.models import Answer, Submission

matplotlib.use("Agg")


def describe_results_with_charts(survey):
    charts_and_text_data = []
    submissions = Submission.objects.filter(survey=survey)
    for question in survey.questions.all():
        question_data = {
            "question_text": question.question_text,
            "pie_chart_base64": None,
            "bar_chart_base64": None,
            "text_answers": [],
            "statistics": [],
            "average": None,
        }

        if question.question_type != TEXT_FIELD:
            options = question.options.all()
            labels = [option.option_text for option in options]
            counts = [
                submissions.filter(answers__selected_options__in=[option.id]).count()
                for option in options
            ]

            question_data["statistics"] = [
                {"option": label, "count": count}
                for label, count in zip(labels, counts, strict=True)
            ]

            try:
                numeric_labels = [float(label) for label in labels]
                total = sum(n * c for n, c in zip(numeric_labels, counts, strict=True))
                count_sum = sum(counts)
                question_data["average"] = total / count_sum if count_sum > 0 else None
            except ValueError:
                question_data["average"] = None

            fig, ax = matplotlib.pyplot.subplots()
            ax.pie(
                counts,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90,
                textprops={"fontsize": 16, "weight": "bold"},
            )
            ax.axis("equal")
            buf = io.BytesIO()
            matplotlib.pyplot.savefig(buf, format="PNG")
            buf.seek(0)
            question_data["pie_chart_base64"] = base64.b64encode(buf.read()).decode(
                "utf-8"
            )
            buf.close()
            matplotlib.pyplot.close(fig)

            fig, ax = matplotlib.pyplot.subplots()
            ax.bar(labels, counts)
            ax.tick_params(axis="x", labelsize=16)
            ax.tick_params(axis="y", labelsize=16)

            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, fontweight="bold", fontsize=16)

            ax.yaxis.set_major_locator(MultipleLocator(1))

            buf = io.BytesIO()
            matplotlib.pyplot.savefig(buf, format="PNG")
            buf.seek(0)
            question_data["bar_chart_base64"] = base64.b64encode(buf.read()).decode(
                "utf-8"
            )
            buf.close()
            matplotlib.pyplot.close(fig)

        else:
            question_data["text_answers"] = [
                answer.answer_text.strip()
                for answer in Answer.objects.filter(question=question).exclude(
                    hide_from_public=True
                )
                if answer.answer_text.strip()
            ]

        charts_and_text_data.append(question_data)
    return charts_and_text_data


def describe_results_csv(survey):
    choice_answers = []
    text_answers = []
    submissions = Submission.objects.filter(survey=survey)
    for question in survey.questions.all():
        if question.question_type != TEXT_FIELD:
            answers = []
            answers.append(["question", question.question_text])
            answers.append(["value:", "count:"])
            for option in question.options.all():
                number_of_selections = submissions.filter(
                    answers__selected_options__in=[option.id]
                ).count()
                answers.append([option.option_text, number_of_selections])
            choice_answers.append(answers)
        else:
            answers = []
            answers.append([question.question_text])
            answers.append(["answer:"])
            answers += [
                [answer.answer_text]
                for answer in Answer.objects.filter(question=question).exclude(
                    hide_from_public=True
                )
            ]
            text_answers.append(answers)
    return choice_answers + text_answers
