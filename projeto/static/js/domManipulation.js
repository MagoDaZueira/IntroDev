let chars = [];

export function renderText(text) {
	const display = document.getElementById("text-display");

	display.innerHTML = "";
	chars = [];

	for (let i = 0; i < text.length; i++) {
		const span = document.createElement("span");
		span.classList.add("char");
		span.textContent = text[i];

		display.appendChild(span);
		chars.push(span);
	}
}

export function updateChar(i, correct) {
	chars[i].classList.remove("correct", "incorrect");
	chars[i].classList.add(correct ? "correct" : "incorrect");
}

export function resetChar(i) {
	chars[i].classList.remove("correct", "incorrect");
}