function showTab(tabId) {
	const tabs = document.querySelectorAll('.tab');
	const tabContents = document.querySelectorAll('.tab-content');
	
	tabs.forEach(tab => {
		tab.classList.remove('active');
	});
	
	tabContents.forEach(content => {
		content.classList.remove('active');
	});
	
	document.querySelector(`.tab[onclick="showTab('${tabId}')"]`).classList.add('active');
	document.getElementById(tabId).classList.add('active');
}