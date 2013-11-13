<TeXmacs|1.0.7.16>

<style|generic>

<\body>
  <doc-data|<doc-title|A Quick Start of TiES>>

  <\table-of-contents|toc>
    <vspace*|1fn><with|font-series|bold|math-font-series|bold|Balabala>
    <datoms|<macro|x|<repeat|<arg|x>|<with|font-series|medium|<with|font-size|1|<space|0.2fn>.<space|0.2fn>>>>>|<htab|5mm>>
    <no-break><pageref|auto-1><vspace|0.5fn>

    <vspace*|1fn><with|font-series|bold|math-font-series|bold|Quick start>
    <datoms|<macro|x|<repeat|<arg|x>|<with|font-series|medium|<with|font-size|1|<space|0.2fn>.<space|0.2fn>>>>>|<htab|5mm>>
    <no-break><pageref|auto-2><vspace|0.5fn>

    <with|par-left|6fn|The parameters for this query
    <datoms|<macro|x|<repeat|<arg|x>|<with|font-series|medium|<with|font-size|1|<space|0.2fn>.<space|0.2fn>>>>>|<htab|5mm>>
    <no-break><pageref|auto-3><vspace|0.15fn>>

    <vspace*|1fn><with|font-series|bold|math-font-series|bold|Not so quick
    start> <datoms|<macro|x|<repeat|<arg|x>|<with|font-series|medium|<with|font-size|1|<space|0.2fn>.<space|0.2fn>>>>>|<htab|5mm>>
    <no-break><pageref|auto-4><vspace|0.5fn>
  </table-of-contents>

  <new-page>

  <section|Balabala>

  TiES is a...

  <section|Quick start>

  Let's start from a simple example:

  <\example>
    I have a lot of logs for Sendmail and I want to search the 10 most
    frequent deffered domains.
  </example>

  If I use the official RESTful API of Elasticsearch, I can type the
  following command:

  <\framed>
    <\shell>
      curl 'my.elasticsearch.host:9200/maillog*' -d '{

      \ \ \ \ "facets": {"domain0": {"terms": {"field": "@fields.toDomain",

      \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ "order":
      "count",

      \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ "size":
      10}}},

      \ \ \ \ "query": {"term": {"@fields.status": "deffered"}},

      \ \ \ \ "size": 0}'
    </shell>
  </framed>

  I think the query is not complicated. But I have to type a very long (and
  multiple lines) command.

  <with|font-series|bold|The factors for this query>

  <\enumerate-numeric>
    <item>The field: the field is ``@fields.toDomain''.

    <item>The size: 10.

    <item>Condition: The content of field ``@field.status'' is ``deffered''.
  </enumerate-numeric>

  <section|Not so quick start>
</body>

<\initial>
  <\collection>
    <associate|language|american>
  </collection>
</initial>

<\references>
  <\collection>
    <associate|auto-1|<tuple|1|2>>
    <associate|auto-2|<tuple|2|2>>
    <associate|auto-3|<tuple|3|2>>
    <associate|auto-4|<tuple|3|2>>
    <associate|quick-start|<tuple|1|?>>
  </collection>
</references>

<\auxiliary>
  <\collection>
    <\associate|toc>
      <vspace*|1fn><with|font-series|<quote|bold>|math-font-series|<quote|bold>|Balabala>
      <datoms|<macro|x|<repeat|<arg|x>|<with|font-series|medium|<with|font-size|1|<space|0.2fn>.<space|0.2fn>>>>>|<htab|5mm>>
      <no-break><pageref|auto-1><vspace|0.5fn>

      <vspace*|1fn><with|font-series|<quote|bold>|math-font-series|<quote|bold>|Quick
      start> <datoms|<macro|x|<repeat|<arg|x>|<with|font-series|medium|<with|font-size|1|<space|0.2fn>.<space|0.2fn>>>>>|<htab|5mm>>
      <no-break><pageref|auto-2><vspace|0.5fn>

      <with|par-left|<quote|6fn>|The factors for this query
      <datoms|<macro|x|<repeat|<arg|x>|<with|font-series|medium|<with|font-size|1|<space|0.2fn>.<space|0.2fn>>>>>|<htab|5mm>>
      <no-break><pageref|auto-3><vspace|0.15fn>>

      <vspace*|1fn><with|font-series|<quote|bold>|math-font-series|<quote|bold>|Not
      so quick start> <datoms|<macro|x|<repeat|<arg|x>|<with|font-series|medium|<with|font-size|1|<space|0.2fn>.<space|0.2fn>>>>>|<htab|5mm>>
      <no-break><pageref|auto-4><vspace|0.5fn>
    </associate>
  </collection>
</auxiliary>