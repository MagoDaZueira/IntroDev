export function sendAttempt(wpm, accuracy, time) {
	htmx.ajax('POST', '/attempt', {
		target: '#main-content',
		swap: 'innerHTML',
		values: {
			wpm: wpm.toFixed(2),
			accuracy: accuracy.toFixed(2),
			duration: time.toFixed(2)
		}
	});
}