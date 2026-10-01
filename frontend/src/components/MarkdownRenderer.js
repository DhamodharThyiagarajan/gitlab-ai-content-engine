"use client";

import { Fragment } from "react";

function InlineMarkdown({ text }) {
  const parts = text.split(/(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\))/g);
  return parts.map((part, index) => {
    if (part.startsWith("`") && part.endsWith("`")) return <code key={index} className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[0.9em] text-orange-200">{part.slice(1, -1)}</code>;
    if (part.startsWith("**") && part.endsWith("**")) return <strong key={index} className="font-semibold text-slate-100">{part.slice(2, -2)}</strong>;
    if (part.startsWith("*") && part.endsWith("*")) return <em key={index}>{part.slice(1, -1)}</em>;
    const link = part.match(/^\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)$/);
    if (link) return <a key={index} href={link[2]} target="_blank" rel="noreferrer" className="text-orange-300 underline underline-offset-4">{link[1]}</a>;
    return <Fragment key={index}>{part}</Fragment>;
  });
}

export default function MarkdownRenderer({ content = "" }) {
  const lines = content.replace(/\r/g, "").split("\n");
  const blocks = [];
  let index = 0;
  while (index < lines.length) {
    const line = lines[index];
    if (!line.trim()) { index += 1; continue; }
    if (line.startsWith("```")) {
      const code = [];
      index += 1;
      while (index < lines.length && !lines[index].startsWith("```")) code.push(lines[index++]);
      index += 1;
      blocks.push(<pre key={`code-${index}`} className="overflow-x-auto rounded-xl border border-slate-700 bg-[#080e19] p-4 text-sm leading-6 text-slate-200"><code>{code.join("\n")}</code></pre>);
      continue;
    }
    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      const Tag = `h${heading[1].length}`;
      blocks.push(<Tag key={`heading-${index}`} className="mt-6 text-xl font-semibold tracking-tight text-slate-100 first:mt-0"><InlineMarkdown text={heading[2]} /></Tag>);
      index += 1; continue;
    }
    if (/^\s*([-*+] |\d+\. )/.test(line)) {
      const ordered = /^\s*\d+\. /.test(line);
      const items = [];
      while (index < lines.length && /^\s*([-*+] |\d+\. )/.test(lines[index])) {
        items.push(lines[index].replace(/^\s*(?:[-*+] |\d+\. )/, "")); index += 1;
      }
      const List = ordered ? "ol" : "ul";
      blocks.push(<List key={`list-${index}`} className={`space-y-2 pl-6 text-slate-300 ${ordered ? "list-decimal" : "list-disc"}`}>{items.map((item, itemIndex) => <li key={itemIndex}><InlineMarkdown text={item} /></li>)}</List>);
      continue;
    }
    if (line.startsWith("> ")) {
      const quote = [];
      while (index < lines.length && lines[index].startsWith("> ")) quote.push(lines[index++].slice(2));
      blocks.push(<blockquote key={`quote-${index}`} className="border-l-2 border-orange-400/70 pl-4 text-slate-300">{quote.map((text, i) => <p key={i}><InlineMarkdown text={text} /></p>)}</blockquote>);
      continue;
    }
    if (/^\s*(---+|___+|\*\*\*+)\s*$/.test(line)) { blocks.push(<hr key={`hr-${index}`} className="border-slate-700" />); index += 1; continue; }
    const paragraph = [line]; index += 1;
    while (index < lines.length && lines[index].trim() && !/^(#{1,4}\s|```|\s*([-*+] |\d+\. )|> )/.test(lines[index])) paragraph.push(lines[index++]);
    blocks.push(<p key={`p-${index}`} className="leading-7 text-slate-300">{paragraph.map((text, i) => <Fragment key={i}>{i > 0 && <br />}<InlineMarkdown text={text.replace(/\s{2,}$/, "")} /></Fragment>)}</p>);
  }
  return <article className="space-y-4 break-words">{blocks}</article>;
}
