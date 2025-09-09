# 🌟 Hello Everyone! Hope You're Doing Great! 🌞

Despite the **very hot weather**, I hope you're all staying cool and energized! 💧😎

---

## 📝 We Have a Small Task Ahead!

Let’s **practice what we’ve covered in the last session** with a hands-on data cleaning exercise. 🛠️

We’ll be working with the dataset:  
📎 **`dirty_cafe_sales.csv`**

🔽 **Download the dataset here:**  
👉 [https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training](https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training)

---

### 🔍 1. Initial Exploration

- Load the dataset into a **pandas DataFrame**.
- Use the following methods to explore:
  - `.info()`
  - `.describe()`
  - `.head()`
  - `.isnull().sum()`
- Get an overview of:
  - ✅ Data types
  - ✅ Missing values
  - ✅ Row counts

---

### 🧹 2. Handle Missing or Placeholder Entries

Identify columns with missing values or placeholders like `"ERROR"`, `"UNKNOWN"`:

- **Item**
- **Quantity**
- **Price Per Unit**
- **Total Spent**
- **Payment Method**
- **Location**
- **Transaction Date**

🔧 Replace `"ERROR"` and `"UNKNOWN"` with **NaN**  
➡️ Then decide: **fill or drop** based on context.

---

### 🔢 3. Impute Logical Relationships

Use the formula:  
**Total Spent = Quantity × Price Per Unit**

Back-calculate missing values:

- **Price Per Unit = Total Spent / Quantity**
- **Quantity = Total Spent / Price Per Unit**  
  (or infer from average price per item group)

✅ Fill missing values using logic  
🗑️ Drop remaining rows with critical missing data if needed

---

### 📅 4. Normalize Date Column

- Convert **Transaction Date** to `datetime` type
- If dates are missing or inconsistent:
  - Sort by transaction date
  - Use **forward-fill** or **backward-fill** to impute
- Ensure all dates are in a **consistent format** recognized by pandas

---

### 🔤 5. Standardize Categorical Columns

Clean up:

- **Item**
- **Payment Method**
- **Location**

✅ Normalize casing (e.g., all lowercase or uppercase)  
✅ Strip whitespace and remove unwanted symbols  
✅ Replace inconsistent labels with consistent ones:

- e.g., `"card"`, `"cash"`, `"unknown"`

---

### 🚫 6. Remove Duplicates

- Use `.drop_duplicates()` to remove duplicate transaction rows
- Ensure **no repeated Transaction ID** values

---

### 🔁 7. Type Conversion & Validation

- Convert numeric columns to correct types:
  - **Quantity**, **Price Per Unit**, **Total Spent** → `float` or `int`
- Check for:
  - ❌ Negative values
  - ❌ Nonsensical entries (e.g., zero quantity, negative price)
- Handle them appropriately

---

### 📊 8. Outlier Detection (Optional)

- Plot or calculate statistical summaries
- Detect outliers in:
  - **Quantity**
  - **Total Spent**
  - **Price Per Unit**
- Decide: **cap, drop, or investigate** further

---

### ⚙️ 9. Feature Engineering & Derived Columns

Optionally create new features:

- **Revenue per Transaction** (= Total Spent)
- **Month**, **Weekday**, or **Hour** from Transaction Date
- Grouped features like:
  - `avg_price_per_item`
  - `location_category`

💡 **Feel free to add your own ideas!** That would be great! 🎉

---

## 📥 Submission Details

📌 We will submit this task via the **Task Submission Form**  
🔗 I’ll share the link shortly

⏰ **Deadline:**  
**Thursday, 31st July – Until 12 AM** 🕛

---

## ❓ Need Help?

Feel free to reach out to:

- **Me** 🧑‍💻
- Or **Eng. Abdul Majeed** 👨‍💼

We’re here to help! 💬✨

Let’s crush this task together! 💪🔥
