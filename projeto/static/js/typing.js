import { sendAttempt } from "./serverConnect.js";
import { renderText, updateChar, resetChar } from "./domManipulation.js";

let input = null;
let container = null;

let startTime = 0;
let started = false;
let index = 0;

let text;
let typedCount = 0;
let correctCount = 0;

function checkAndInit() {
	const typingArea = document.getElementById('typing-container');
	if (typingArea) {
		container = typingArea;
		init();
	}
}

document.addEventListener("htmx:afterSettle", checkAndInit);
checkAndInit();

function init() {
	input = document.getElementById('hidden-input');
	text = container.dataset.text;

	renderText(text);

	input.addEventListener("keydown", (e) => {
		if (e.key === "Backspace") {
			handleBackspace();
		}
		else if (e.key.length === 1) {
			handleChar(e.key);
		}
	});
}

function startGame() {
	started = true;
	startTime = Date.now();
	index = 0;
}

function endGame() {
	started = false;
	const time = (Date.now() - startTime) / 1000;
	const wpm = ((text.length / 5) / time) * 60;
	const accuracy = (correctCount / typedCount) * 100;

	sendAttempt(wpm, accuracy, time);
}

function handleChar(key) {
	if (!started) {
		startGame();
	}

	if (index >= text.length) return;

	const isCorrect = text[index] === key;

	typedCount++;
	correctCount += isCorrect;

	updateChar(index, isCorrect);

	index++;

	if (index >= text.length) {
		endGame();
	}
}

function handleBackspace() {
	if (index <= 0) return;
	index--;
	resetChar(index);
}