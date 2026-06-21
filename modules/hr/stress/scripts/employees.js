import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL;
const AREA_ID = parseInt(__ENV.SEED_AREA_ID || "1");

export const options = {
  vus: 20,
  duration: "30s",
  thresholds: {
    http_req_duration: ["p(95)<1000"],
    http_req_failed: ["rate<0.01"],
  },
};

export default function () {
  check(http.get(`${BASE_URL}/employees`), {
    "list employees 200": (r) => r.status === 200,
    "list employees is array": (r) => Array.isArray(r.json()),
  });

  check(http.get(`${BASE_URL}/employees/1`), {
    "get employee 200 or 404": (r) => r.status === 200 || r.status === 404,
  });

  check(http.get(`${BASE_URL}/areas`), {
    "list areas 200": (r) => r.status === 200,
  });

  // Write path — unique email per VU+iteration avoids constraint violations
  const uid = `${__VU}-${__ITER}`;
  check(
    http.post(
      `${BASE_URL}/employees`,
      JSON.stringify({
        name: `LoadUser ${uid}`,
        email: `load-${uid}@stress.test`,
        role: "JUNIOR",
        salary: 5000,
        area_id: AREA_ID,
      }),
      { headers: { "Content-Type": "application/json" } }
    ),
    { "hire employee 201": (r) => r.status === 201 }
  );

  sleep(0.1);
}
