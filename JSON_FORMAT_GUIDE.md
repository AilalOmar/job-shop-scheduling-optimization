# JSON Format Guide for Job Shop Scheduling Problems

## 📋 Complete JSON Structure

```json
{
  "name": "instance_name",
  "n_machines": 3,
  "n_jobs": 3,
  "bks": 7,
  "jobs": [
    {
      "id": 0,
      "operations": [
        {"machine": 0, "duration": 3},
        {"machine": 1, "duration": 2}
      ]
    }
  ]
}
```

---

## 🔑 Field Descriptions

### Top-Level Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | string | ✅ Yes | Problem instance name | "example_3x3" |
| `n_machines` | integer | ✅ Yes | Total number of machines | 3 |
| `n_jobs` | integer | ✅ Yes | Total number of jobs | 3 |
| `bks` | integer/null | ❌ No | Best-Known Solution (optional) | 7 or null |
| `jobs` | array | ✅ Yes | Array of job objects | [...] |

### Job Object Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `id` | integer | ✅ Yes | Job identifier (0-indexed) | 0, 1, 2 |
| `operations` | array | ✅ Yes | Array of operation objects | [...] |

### Operation Object Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `machine` | integer | ✅ Yes | Machine ID (0-indexed) | 0, 1, 2 |
| `duration` | integer | ✅ Yes | Processing time (positive integer) | 3, 5, 10 |

---

## 📌 Important Rules

### 1. **Machine Numbering (0-indexed)**
- Machines are numbered from **0** to **n_machines-1**
- ✅ For 3 machines: use 0, 1, 2
- ❌ NOT: 1, 2, 3

### 2. **Job Numbering (0-indexed)**
- Jobs are numbered from **0** to **n_jobs-1**
- ✅ For 3 jobs: use id 0, 1, 2
- ❌ NOT: 1, 2, 3

### 3. **Operation Order Matters**
- Operations in the `operations` array are executed **in sequence**
- First operation must finish before second can start
- Example:
  ```json
  "operations": [
    {"machine": 0, "duration": 3},  // Runs first
    {"machine": 1, "duration": 2},  // Runs second (after first finishes)
    {"machine": 2, "duration": 5}   // Runs third (after second finishes)
  ]
  ```

### 4. **Each Job Can Visit Each Machine Only Once**
- A job cannot have two operations on the same machine
- ✅ Correct: Machine 0, then Machine 1, then Machine 2
- ❌ Wrong: Machine 0, then Machine 1, then Machine 0 again

---

## 📝 Complete Examples

### Example 1: 3×3 Problem (Simple)

**Description:** 3 jobs, 3 machines, known optimal makespan = 7

```json
{
  "name": "simple_3x3",
  "n_machines": 3,
  "n_jobs": 3,
  "bks": 7,
  "jobs": [
    {
      "id": 0,
      "operations": [
        {"machine": 0, "duration": 3},
        {"machine": 1, "duration": 2},
        {"machine": 2, "duration": 2}
      ]
    },
    {
      "id": 1,
      "operations": [
        {"machine": 1, "duration": 2},
        {"machine": 2, "duration": 1},
        {"machine": 0, "duration": 1}
      ]
    },
    {
      "id": 2,
      "operations": [
        {"machine": 2, "duration": 3},
        {"machine": 0, "duration": 1},
        {"machine": 1, "duration": 2}
      ]
    }
  ]
}
```

**This means:**
- **Job 0:**
  - Operation 1: Machine 0 for 3 time units
  - Operation 2: Machine 1 for 2 time units
  - Operation 3: Machine 2 for 2 time units
- **Job 1:**
  - Operation 1: Machine 1 for 2 time units
  - Operation 2: Machine 2 for 1 time unit
  - Operation 3: Machine 0 for 1 time unit
- **Job 2:**
  - Operation 1: Machine 2 for 3 time units
  - Operation 2: Machine 0 for 1 time unit
  - Operation 3: Machine 1 for 2 time units

---

### Example 2: 4×4 Problem (Medium)

**Description:** 4 jobs, 4 machines, unknown optimal

```json
{
  "name": "medium_4x4",
  "n_machines": 4,
  "n_jobs": 4,
  "bks": null,
  "jobs": [
    {
      "id": 0,
      "operations": [
        {"machine": 0, "duration": 5},
        {"machine": 1, "duration": 3},
        {"machine": 2, "duration": 4},
        {"machine": 3, "duration": 2}
      ]
    },
    {
      "id": 1,
      "operations": [
        {"machine": 1, "duration": 4},
        {"machine": 0, "duration": 2},
        {"machine": 3, "duration": 5},
        {"machine": 2, "duration": 3}
      ]
    },
    {
      "id": 2,
      "operations": [
        {"machine": 2, "duration": 3},
        {"machine": 3, "duration": 4},
        {"machine": 0, "duration": 2},
        {"machine": 1, "duration": 5}
      ]
    },
    {
      "id": 3,
      "operations": [
        {"machine": 3, "duration": 2},
        {"machine": 2, "duration": 5},
        {"machine": 1, "duration": 3},
        {"machine": 0, "duration": 4}
      ]
    }
  ]
}
```

---

### Example 3: 2×5 Problem (Asymmetric)

**Description:** 2 jobs with different number of operations

```json
{
  "name": "asymmetric_2x5",
  "n_machines": 5,
  "n_jobs": 2,
  "bks": null,
  "jobs": [
    {
      "id": 0,
      "operations": [
        {"machine": 0, "duration": 4},
        {"machine": 1, "duration": 3},
        {"machine": 2, "duration": 5},
        {"machine": 3, "duration": 2},
        {"machine": 4, "duration": 6}
      ]
    },
    {
      "id": 1,
      "operations": [
        {"machine": 4, "duration": 3},
        {"machine": 3, "duration": 4},
        {"machine": 2, "duration": 2},
        {"machine": 1, "duration": 5},
        {"machine": 0, "duration": 3}
      ]
    }
  ]
}
```

---

## ✅ Validation Checklist

Before uploading your JSON file, verify:

- [ ] All machine IDs are between 0 and (n_machines - 1)
- [ ] All job IDs are between 0 and (n_jobs - 1)
- [ ] All durations are positive integers (> 0)
- [ ] Jobs array has exactly n_jobs elements
- [ ] Each job has at least 1 operation
- [ ] No job visits the same machine twice
- [ ] JSON syntax is valid (use a JSON validator)
- [ ] File encoding is UTF-8

---

## 🔧 Common Mistakes

### ❌ Wrong: 1-indexed machines
```json
{
  "n_machines": 3,
  "jobs": [{
    "id": 0,
    "operations": [
      {"machine": 1, "duration": 3},  // ❌ Should be 0
      {"machine": 2, "duration": 2},  // ❌ Should be 1
      {"machine": 3, "duration": 5}   // ❌ Should be 2
    ]
  }]
}
```

### ✅ Correct: 0-indexed machines
```json
{
  "n_machines": 3,
  "jobs": [{
    "id": 0,
    "operations": [
      {"machine": 0, "duration": 3},  // ✅ Correct
      {"machine": 1, "duration": 2},  // ✅ Correct
      {"machine": 2, "duration": 5}   // ✅ Correct
    ]
  }]
}
```

---

### ❌ Wrong: Visiting same machine twice
```json
{
  "id": 0,
  "operations": [
    {"machine": 0, "duration": 3},
    {"machine": 1, "duration": 2},
    {"machine": 0, "duration": 5}   // ❌ Machine 0 already used
  ]
}
```

### ✅ Correct: Each machine once
```json
{
  "id": 0,
  "operations": [
    {"machine": 0, "duration": 3},
    {"machine": 1, "duration": 2},
    {"machine": 2, "duration": 5}   // ✅ Each machine used once
  ]
}
```

---

## 🎯 Quick Template Generator

Copy and modify this template:

```json
{
  "name": "YOUR_PROBLEM_NAME",
  "n_machines": NUMBER_OF_MACHINES,
  "n_jobs": NUMBER_OF_JOBS,
  "bks": null,
  "jobs": [
    {
      "id": 0,
      "operations": [
        {"machine": 0, "duration": DURATION},
        {"machine": 1, "duration": DURATION}
      ]
    },
    {
      "id": 1,
      "operations": [
        {"machine": 0, "duration": DURATION},
        {"machine": 1, "duration": DURATION}
      ]
    }
  ]
}
```

---

## 📁 Example Files Provided

In the `jsp-solver` folder, you'll find:

- `example_3x3.json` - Simple 3×3 problem (optimal = 7)
- `example_4x4.json` - Medium 4×4 problem

You can use these as templates or upload them directly to test the app!

---

## 💡 Tips

1. **Start Small:** Test with 2×2 or 3×3 before trying larger problems
2. **Use BKS:** If you know the optimal solution, include it in the `bks` field to see the gap
3. **Copy Format:** Use the provided examples as templates
4. **Validate JSON:** Use online JSON validators (jsonlint.com) before uploading
5. **Machine Order:** Machines can be visited in any order (it's the sequence that matters)

---

## 🚀 How to Use in the App

1. Open the Streamlit app (http://localhost:8501)
2. Select **"Charger JSON"** from the radio buttons
3. Click **"Browse files"** or drag-and-drop your JSON file
4. Click **"🚀 Résoudre avec Recuit Simulé"**
5. View the results!

---

**Need more help? See the app's built-in example viewer for the JSON format!**
