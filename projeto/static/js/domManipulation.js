let chars = [];
let cursor = null;

export function renderText(text) {
	const display = document.getElementById("text-display");

	display.innerHTML = "";
	chars = [];
	cursor = document.getElementById("cursor");

	for (let i = 0; i < text.length; i++) {
		const span = document.createElement("span");
		span.classList.add("char");
		span.textContent = text[i];
		
		display.appendChild(span);
		chars.push(span);
	}

	updateCursor(0);
}

export function updateChar(i, correct) {
	if (!correct && chars[i].innerText === " ") {
		chars[i].innerText = "_";
		chars[i].style.wordBreak = "break-all";
	}
	chars[i].classList.remove("correct", "incorrect");
	chars[i].classList.add(correct ? "correct" : "incorrect");
}

export function resetChar(i) {
	if (chars[i].innerText === "_") {
		chars[i].innerText = " ";
		chars[i].style.wordBreak = "normal";
	}
	chars[i].classList.remove("correct", "incorrect");
}

export function updateCursor(i) {
	const rect = chars[i].getBoundingClientRect();
	cursor.style.left = rect.left + "px";
	cursor.style.top = rect.top + "px";
}