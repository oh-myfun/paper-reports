## Description: <br>
Convert academic papers into structured Chinese reading reports with original figures. Supports arXiv HTML and local PDF inputs. For arXiv links, HTML mode is preferred for textual accuracy. Use when the user asks to summarize, read, analyze, or create a reading report for an academic paper (PDF file or arXiv link). <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[nuaalixu](https://clawhub.ai/user/nuaalixu) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers, researchers, and students use this skill to turn an arXiv link, other paper HTML page, or local PDF into a structured Chinese reading report with selected original figures. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The workflow can contact arXiv or another user-provided paper URL and download paper assets. <br>
Mitigation: Use trusted paper sources and review non-arXiv URLs before allowing network access. <br>
Risk: The workflow may install missing Python packages before processing PDFs or inline SVG figures. <br>
Mitigation: Review package installation commands before running them in the agent environment. <br>
Risk: The workflow creates report, figure, page-image, and extracted-text files in the workspace. <br>
Mitigation: Run the skill in an intended workspace and review generated files before sharing them. <br>
Risk: PDF visual extraction and paper summarization can misread figures, tables, formulas, or numeric values. <br>
Mitigation: Check important claims, figures, formulas, and numeric values against the source paper. <br>


## Reference(s): <br>
- [HTML Mode Workflow](path-html.md) <br>
- [PDF Mode Workflow](path-pdf.md) <br>
- [Markdown Report Template](report-template.md) <br>
- [HTML Report Template](report-template.html) <br>
- [ClawHub Skill Page](https://clawhub.ai/nuaalixu/paper-report) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, HTML, Files, Shell commands, Guidance] <br>
**Output Format:** [Chinese HTML or Markdown reading report with embedded or linked figure images.] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May create report, figure, page image, and extracted text files in the workspace.] <br>

## Skill Version(s): <br>
2.0.1 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
