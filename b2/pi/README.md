# Block 2, second half: the same task with pi (RStudio on Nuvolos)

In the first half you cleaned the World Bank extract cell by cell with Gemini in Colab. Now you
give the same task, [`TASK.md`](TASK.md), to **pi**, a coding agent, and review what it did.

Key, pi and RStudio are set up on Nuvolos. If something does not work, see
[`SETUP.md`](../../SETUP.md) (also for working on your own laptop).

## 1. Go to the files and put them under git

On Nuvolos the course files are in `/files/pee_2026`. In RStudio, open the **Terminal** tab
(Terminal → New Terminal) and run:

```bash
cd /files/pee_2026/b2
git config --global user.name >/dev/null || git config --global user.name "Student"
git config --global user.email >/dev/null || git config --global user.email "student@example.com"
git init -q && git add -A && git commit -qm "start"
```

Now the folder is a git repository, so you can see later exactly what pi changed.

On your own laptop: `git clone https://github.com/umatter/pe_materials.git` and `cd pe_materials/b2`
instead (a clone is already a git repository).

## 2. The key and pi

On Nuvolos, load the course key into this terminal (once per terminal; on your own laptop
skip this line, see `SETUP.md`), then check:

```bash
export OPENROUTER_API_KEY="$(cat /secrets/OPENROUTER_API_KEY)"
pi --version
[ -n "$OPENROUTER_API_KEY" ] && echo TRUE || echo FALSE
```

## 3. Give pi the task

Start pi inside the `b2` folder:

```bash
pi --model openrouter/anthropic/claude-haiku-5.5
```

and type:

```text
Read pi/TASK.md and do it. Save clean_wdi.R and wdi_clean.csv in this folder. Run the script with Rscript and check the result.
```

Watch what it does: which files it reads, what it writes, which commands it runs, how it reacts
to an error. Leave pi with `/quit` (or Ctrl+C twice).

**pi does not ask before it edits a file or runs a command.** On the course VM it is contained to your machine, but your other course files are there too. On
your own laptop, read the safety notes in `SETUP.md` first.

## 4. Review what it did

```bash
git status                  # which files are new or changed?
git diff                    # what changed in files that already existed?
Rscript clean_wdi.R         # does the script run for you?
Rscript pi/check.R          # the same self-checks as in the Colab notebook
```

Open `clean_wdi.R` in RStudio and read it. Did pi do all six steps the way the task asks? Did it
tell you anything it had not checked?

## 5. Notes for the debrief

Compare with the Colab half, two or three lines each:

1. **Control:** where did you decide, and where did the agent decide for you?
2. **Speed:** which half got to a passing `check.R` faster?
3. **What broke**, and who noticed it: you, the agent, or the checks?
4. **What you still had to check yourself.**
5. **Which mistake would you not have caught** without the self-checks?

If you are done early: run it again with `--model openrouter/deepseek/deepseek-v4.1-flash`
(delete `clean_wdi.R` and `wdi_clean.csv` first) and compare the two scripts.
