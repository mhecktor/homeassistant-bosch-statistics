const http = require("http");
const fs = require("fs");

function getCurrentMonth(data) {
	const now = new Date();
	// API uses 0-based months
	return {
		applianceConsumptionData: [
			data.applianceConsumptionData.find(
				(m) =>
					m.associatedMonth.year === now.getFullYear() &&
					m.associatedMonth.month === now.getMonth()
			)]
	}
}

const server = http.createServer(async (req, res) => {
	console.log(req)
	if (req.method === "GET" && req.url === "/stats") {
		fs.readFile("./data.json", "utf8", function(err, data) {
			console.log(JSON.parse(data))
			const month = getCurrentMonth(JSON.parse(data));

			if (!month) {

				res.writeHead(404, { "Content-Type": "application/json" });
				res.end(JSON.stringify({ error: "No data for current month" }));
				return;
			}

			res.writeHead(200, { "Content-Type": "application/json" });
			res.end(JSON.stringify(month, null, 2));

		})
	} else {
		res.writeHead(404);
		res.end();
	}
});

server.listen(3000, () => console.log("Listening on http://localhost:3000/stats"));
