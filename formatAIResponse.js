function formatAIResponse(text) {

    const codeParts = [];
    const codeToken = "__CODE_BLOCK_";

    /* Find code blocks */

    let safeText = text.replace(
        /```(?:[a-zA-Z0-9_+#.-]+)?\s*\n?([\s\S]*?)```/g,
        function (_, code) {

            const index = codeParts.length;

            codeParts.push(
                code.replace(
                    /^\n|\n$/g,
                    ""
                )
            );

            return "\n" + codeToken + index + "\n";
        }
    );

    const lines = safeText.split("\n");

    let html = "";
    let paragraph = [];

    function flushParagraph() {

        if (paragraph.length > 0) {

            html +=
                "<p>" +
                formatInline(
                    paragraph.join("\n")
                ).replace(
                    /\n/g,
                    "<br>"
                ) +
                "</p>";

            paragraph = [];
        }
    }

    lines.forEach(function (line) {

        /* Headings */

        const heading = line.match(
            /^\s*(#{1,3})\s+(.+)$/
        );

        if (heading) {

            flushParagraph();

            const level =
                heading[1].length;

            html +=
                "<h" +
                level +
                ">" +
                formatInline(
                    heading[2]
                ) +
                "</h" +
                level +
                ">";

            return;
        }


        /* Code block */

        const codeMatch = line.match(
            /^\s*__CODE_BLOCK_(\d+)\s*$/
        );

        if (codeMatch) {

            flushParagraph();

            const index =
                Number(codeMatch[1]);

            const rawCode =
                codeParts[index];

            const highlightedCode =
                hljs.highlightAuto(
                    rawCode
                ).value;

            html += `
                <div class="code-block">

                    <div class="code-header">

                        <button
                            class="code-copy-btn"
                            onclick="copyCode(this)">
                            Copy
                        </button>

                    </div>

                    <pre><code>${highlightedCode}</code></pre>

                </div>
            `;

            return;
        }


        /* Empty line */

        if (line.trim() === "") {

            flushParagraph();

        } else {

            paragraph.push(line);
        }

    });

    flushParagraph();

    return (
        html ||
        formatInline(text)
    );
}