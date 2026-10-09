# Demo Script — GitLab AI Content Engine

The demonstration is divided into seven parts, covering the main project components, AI workflow, testing, and documentation.

## AI Workflow (0–5 minutes)

**Focus:** Multi-stage AI content-generation workflow.

* Introduce the purpose of the AI workflow.
* Explain how the workflow receives task inputs and uses the configured language model.
* Demonstrate the Context Reader and explain its role in extracting source-grounded information.
* Explain the Documentation Writer and Technical Reviewer.
* Describe the Tone Optimizer and Publishing Coordinator.
* Show how the five specialized agents work sequentially to prepare the final content.

## Backend and API (5–9 minutes)

**Focus:** Backend implementation and API integration.

* Explain the role of the backend in the application.
* Show the relevant API implementation in `backend/app/api/reviews.py`.
* Explain how the application handles review-related operations, based on the actual implementation.
* Demonstrate a real API request and response, if available.
* Explain how the API layer interacts with the AI workflow.

## AI Agent Architecture (9–13 minutes)

**Focus:** Agent responsibilities and task coordination.

* Open `backend/ai/agents/crew.py`.
* Explain the `build_crew` function.
* Introduce the five agents: Context Reader, Documentation Writer, Technical Reviewer, Tone Optimizer, and Publishing Coordinator.
* Explain how each agent has a specific role and goal.
* Demonstrate how tasks are organized using `Process.sequential`.
* Explain how context from previous tasks can be passed to subsequent tasks.

## Application Workflow and Output (13–16 minutes)

**Focus:** Processing task inputs and generating content.

* Show how the application invokes the AI workflow in `backend/ai/workflow.py`.
* Explain how task inputs are passed into the workflow.
* Demonstrate the actual workflow using a prepared sample input.
* Show the generated output and explain its structure.
* Explain how the final stage prepares the content for output.

## Testing and API Testing (16–21 minutes)

**Focus:** Validating application behavior and API functionality.

* Explain the purpose of automated testing.
* Show `tests/ai_output_tests/test_ai_workflow.py`.
* Demonstrate relevant test cases and expected-agent or output checks.
* Show the actual test results confirming that 25 out of 25 tests passed.
* Demonstrate API testing using the project's actual API testing file or tool.
* Explain how the team checks responses and validates expected behavior.

## Architecture and Workflow Documentation (21–24 minutes)

**Focus:** Explaining and documenting the project design.

* Open `docs/architecture.md`.
* Explain the architecture diagram and the main project components.
* Describe the sequential AI workflow and the responsibilities of the five agents.
* Explain how technical documentation helps developers understand and maintain the project.
* Show the `docs/demo_script.md` file and explain how it supports the project demonstration.

## Conclusion and Future Enhancements (24–27 minutes)

**Focus:** Project summary and possible improvements.

* Summarize the purpose of the GitLab AI Content Engine.
* Highlight the benefits of using five specialized AI agents.
* Explain the importance of source-grounded content, review, and testing.
* Summarize the testing results.
* Discuss possible future enhancements, such as improved workflow monitoring, prompt version management, stronger validation, and additional integrations where appropriate.
* Thank the audience and invite feedback.

---

## Presenter Notes

* Demonstrate only features that are implemented in the current project.
* Use the actual sample input, commands, and API requests from the repository.
* Show the real test output when reporting the 25/25 result.
* Do not expose API keys, `.env` values, or other sensitive information.
* Adjust the timing according to the number of presenters and the actual demonstration.
