;;;;;;;;;; kmap-mode for 22key keymaps ;;;;;;;;;

(defvar kmap-font-lock-defaults
  `((("\\*\\|shifted" . font-lock-constant-face)
     ("\\." . font-lock-builtin-face)
     )))

(define-derived-mode kmap-mode fundamental-mode "kmap"
  "kmap mode is a major mode for editing 22key keymap files"
  (setq font-lock-defaults kmap-font-lock-defaults)
  ;;make comments work
  (setq comment-start "//")
  (setq comment-end "")
  (modify-syntax-entry ?/ ". 12b" kmap-mode-syntax-table)
  (modify-syntax-entry ?\n "> b" kmap-mode-syntax-table)
  ;;periods are parts of words
  (modify-syntax-entry ?. "w" kmap-mode-syntax-table)
  ;;asterisks are not, we can jump to them with forward-word
  (modify-syntax-entry ?* "." kmap-mode-syntax-table)
  ;;quotes are parts of words, to prevent string highlighting
  (modify-syntax-entry ?\" "w" kmap-mode-syntax-table)
  ;;A gnu-correct program will have some sort of hook call here.
  )

(provide 'kmap-mode)
(add-to-list 'auto-mode-alist '("\\.kmap\\'" . kmap-mode))

