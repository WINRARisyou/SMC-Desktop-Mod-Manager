var assetsURL;
function parseModData(mod, id) {
	return {
		filename: mod.FileName || 'Cannot Download',
		name: mod.Name || 'Unnamed Mod',
		author: mod.Author || 'Unknown Author',
		id: id || '???',
		version: mod.Version || 'Unknown Version',
		gameVersion: mod.GameVersion || 'Unknown Game Version',
		description: mod.Description || 'No Description',
	};
}

function displayMods(mods) {
	const modList = document.getElementById('mod-list');
	modList.innerHTML = '';
	if (mods.length === 0) {
		modList.innerHTML = '<p>No valid mods found. :/</p>';
		return;
	}

	mods.forEach((mod) => {
		let sanatize = function (str) {
			str = str.replace(/<[^>]*>?/gm, ''); // nuke any html tags
			str = str.replace(/<script[^>]*>.*<\/script>/gm, ''); // nuke any script tags that survived the first bomb
			str = str.replace(/on\w+=".*"/gm, ''); // nuke any on* events
			str = str.replace(/href=".*"/gm, ''); // nuke any hrefs
			str = str.replace(/src=".*"/gm, ''); // nuke any srcs
			str = str.replace(/\n/g, '<br>').replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;'); // convert escaped characters
			return str
		}
		const modItem = document.createElement('div');
		modItem.className = 'mod-item';
		let iconURL;
		if (assetsURL.endsWith("/")) {
			iconURL = `${assetsURL}/${mod.id}`;
		} else {
			iconURL = `${assetsURL}${mod.id}`;
		}
		let modContent = `
			<h3>${sanatize(mod.name)}</h3>
			<img class="mod-icon" src="${iconURL}/icon.png" alt="" />
			<h3>Author: ${sanatize(mod.author)}</h3>
			<p><strong>Version:</strong> ${sanatize(mod.version)}</p>
			<p><strong>Game Version:</strong> ${sanatize(mod.gameVersion)}</p>
			<p><strong>Description:<br></strong>${sanatize(mod.description)}</p>
			<button onclick="downloadMod('${sanatize(mod.filename)}')">Download</button>
		`;

		if (location.href.endsWith("github.dev/") || location.href.startsWith("http://localhost")) {
			modContent = `<p><strong>Mod ID:</strong> ${sanatize(mod.id)}</p>` + modContent;
		}

		modItem.innerHTML = modContent;
		modList.appendChild(modItem);
	});
}

function downloadMod(filename) {
	if (!assetsURL) {
		alert('No assets URL found. :/');
		return;
	}
	
	if (filename == "Cannot Download") {
		alert("Couldn't download this mod at this time. :/")
	}

	const downloadLink = document.createElement('a');
	if (assetsURL.endsWith("/")) {
		downloadLink.href = `${assetsURL}/${filename}`;
	} else {
		downloadLink.href = `${assetsURL}${filename}`;
	}
	downloadLink.download = filename;
	downloadLink.click();
}

/**
 * @param {string} modlistURL The URL of the modlist
**/
function getOnlineModList(modlistURL) {
	fetch(modlistURL)
		.then(response => {
			if (!response.ok) {
				document.getElementById('mod-list').innerHTML = '<p>Failed to load mod list :/</p>';
				throw new Error(`Could not resolve mod list, HTTP error: ${response.status}`);
			}
			return response.json();
		})
		.then(data => {
			let assetURLs = data.assetsURL;
			let assetURLPromises = assetURLs.map((url, index) => {
				if (!url.startsWith("https://archive.org")) {
					return fetch(url)
						.then(response => {
							if (response.ok) {
								return { url, index };
							} else {
								console.log(`Assets URL #${index + 1} (${url}) is down or invalid.`);
								return null;
							}
						})
						.catch(error => { console.error(`Failed to resolve assets URL #${index + 1} (${url}), error: ${error}`); return null; });
				} else {
					return fetch(`${url}/stat.json`)
						.then(response => {
							if (response.ok) {
								return { url, index };
							} else {
								console.log(`Assets URL #${index + 1} (${url}) is down or invalid.`);
								return null;
							}
						})
						.catch(error => { console.error(`Failed to resolve assets URL #${index + 1} (${url}), error: ${error}`); return null; });
				}
			});

			Promise.all(assetURLPromises).then(results => {
				for (let result of results) {
					if (result && typeof assetsURL === "undefined") {
						console.log(`Using Assets URL #${result.index + 1}: ${result.url}`);
						assetsURL = result.url;
						break;
					}
				}

				const parsedModData = [];
				for (let key in data) {
					// Ignore assetsURL
					if (key !== "assetsURL") {
						parsedModData.push(parseModData(data[key], key));
					}
				}

				if (parsedModData.length === 0) {
					document.getElementById('mod-list').innerHTML = '<p>No mods found. :p</p>';
				} else {
					displayMods(parsedModData);
				}
			});
		})
		.catch(error => {document.getElementById('mod-list').innerHTML='<p>Failed to resolve mod list. :/</p>'; console.error(`Failed to resolve mod list data, error: ${error}`)});
}
getOnlineModList("files/modlist.json")