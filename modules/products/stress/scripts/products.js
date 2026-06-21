import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL;

export const options = {
  vus: 20,
  duration: "30s",
  thresholds: {
    http_req_duration: ["p(95)<500"],
    http_req_failed: ["rate<0.01"],
  },
};

export default function () {
  // Read paths
  check(http.get(`${BASE_URL}/products`), {
    "list products 200": (r) => r.status === 200,
    "list products is array": (r) => Array.isArray(r.json()),
  });

  check(http.get(`${BASE_URL}/products/1`), {
    "get product 200 or 404": (r) => r.status === 200 || r.status === 404,
  });

  // Write path — unique name per VU+iteration avoids name/category uniqueness violations
  const uid = `${__VU}-${__ITER}`;
  check(
    http.post(
      `${BASE_URL}/products`,
      JSON.stringify({
        name: `StressProduct ${uid}`,
        category: "stress",
        price: 9.99,
        stock: 100,
      }),
      { headers: { "Content-Type": "application/json" } }
    ),
    { "create product 201": (r) => r.status === 201 }
  );

  sleep(0.1);
}
